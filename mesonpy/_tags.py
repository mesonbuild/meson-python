# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>

import abc
import re

from typing import Any, Optional

from mesonpy._compat import Literal, Sequence


class Tag(abc.ABC):
    @abc.abstractmethod
    def __init__(self, value: str) -> None: ...

    @abc.abstractmethod
    def __str__(self) -> str: ...

    @property
    @abc.abstractmethod
    def python(self) -> Optional[str]:
        """Python tag."""

    @property
    @abc.abstractmethod
    def abi(self) -> str:
        """ABI tag."""


class StableABITag(Tag):
    _REGEX = re.compile(r'^abi(?P<abi_number>[0-9]+)$')

    def __init__(self, value: str) -> None:
        match = self._REGEX.match(value)
        if not match:
            raise ValueError(f'Invalid PEP 3149 stable ABI tag, expecting pattern `{self._REGEX.pattern}`')
        self._abi_number = int(match.group('abi_number'))

    @property
    def abi_number(self) -> int:
        return self._abi_number

    def __str__(self) -> str:
        return f'abi{self.abi_number}'

    @property
    def python(self) -> Literal[None]:
        return None

    @property
    def abi(self) -> str:
        return f'abi{self.abi_number}'

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and other.abi_number == self.abi_number

    def __hash__(self) -> int:
        return hash(str(self))


class InterpreterTag(Tag):
    def __init__(self, value: str) -> None:
        parts = value.split('-')
        if len(parts) < 2:
            raise ValueError(
                'Invalid PEP 3149 interpreter tag, expected at '
                f'least 2 parts but got {len(parts)}'
            )

        # On Windows, file extensions look like `.cp311-win_amd64.pyd`, so the
        # implementation part (`cpython-`) is different from Linux. Handle that here:
        if parts[0].startswith('cp3'):
            parts.insert(0, 'cpython')
            parts[1] = parts[1][2:]  # strip 'cp'

        self._implementation = parts[0]
        self._interpreter_version = parts[1]
        self._additional_information = parts[2:]

        if self.implementation != 'cpython' and not self.implementation.startswith('pypy'):
            raise NotImplementedError(
                f'Unknown Python implementation: {self.implementation}. '
                'Please report this to https://github.com/FFY00/mesonpy/issues '
                'and include information about the Python distribution you are using.'
            )

    @property
    def implementation(self) -> str:
        return self._implementation

    @property
    def interpreter_version(self) -> str:
        return self._interpreter_version

    @property
    def additional_information(self) -> Sequence[str]:
        return tuple(self._additional_information)

    def __str__(self) -> str:
        return '-'.join((
            self.implementation,
            self.interpreter_version,
            *self.additional_information,
        ))

    @property
    def python(self) -> str:
        if self.implementation == 'cpython':
            # The Python tag for CPython does not seem to include the flags suffixes.
            return f'cp{self.interpreter_version}'.rstrip('dmu')
        elif self.implementation.startswith('pypy'):
            return f'pp{self.implementation[4:]}'
            # XXX: FYI older PyPy version use the following model
            #      pp{self.implementation[4]}{self.interpreter_version[2:]}
        raise ValueError(f'Unknown implementation: {self.implementation}')

    @property
    def abi(self) -> str:
        if self.implementation == 'cpython':
            return f'cp{self.interpreter_version}'
        elif self.implementation.startswith('pypy'):
            return f'{self.implementation}_{self.interpreter_version}'
        raise ValueError(f'Unknown implementation: {self.implementation}')

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, self.__class__)
            and other.implementation == self.implementation
            and other.interpreter_version == self.interpreter_version
        )

    def __hash__(self) -> int:
        return hash(str(self))
