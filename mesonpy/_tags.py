# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>

import abc
import re
import sys
import warnings

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


class LinuxInterpreterTag(Tag):
    def __init__(self, value: str) -> None:
        parts = value.split('-')
        if len(parts) < 2:
            raise ValueError(
                'Invalid PEP 3149 interpreter tag, expected at '
                f'least 2 parts but got {len(parts)}'
            )

        self._implementation = parts[0]
        self._interpreter_version = parts[1]
        self._additional_information = parts[2:]

        if self.implementation not in ('cpython', 'pypy', 'pypy3'):
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
        elif self.implementation in ('pypy', 'pypy3'):
            interpreter_version = f'{sys.version_info[0]}{sys.version_info[1]}'
            return f'pp{interpreter_version}'
        raise ValueError(f'Unknown implementation: {self.implementation}')

    @property
    def abi(self) -> str:
        # XXX: This is a bit flimsy and needs custom logic to support each case,
        #      but currently there's no better way to do it.
        if self.implementation == 'cpython':
            return f'cp{self.interpreter_version}'
        elif self.implementation == 'pypy':
            return f'pypy_{self.interpreter_version}'
        elif self.implementation == 'pypy3':
            return f'pypy3_{self.interpreter_version}'
        raise ValueError(f'Unknown implementation: {self.implementation}')

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, self.__class__)
            and other.implementation == self.implementation
            and other.interpreter_version == self.interpreter_version
        )

    def __hash__(self) -> int:
        return hash(str(self))


class WindowsInterpreterTag(Tag):
    def __init__(self, value: str) -> None:
        # XXX: This is not actually standardized, so our implementation relies
        #      on observing how the current software behaves!
        self._parts = value.split('-')
        if len(self.parts) != 2:
            warnings.warn(
                'Unexpected native module tag name, the ABI dectection might be broken. '
                'Please report this to https://github.com/FFY00/mesonpy/issues '
                'and include information about the Python distribution you are using.'
            )

    @property
    def parts(self) -> Sequence[str]:
        return tuple(self._parts)

    def __str__(self) -> str:
        return '-'.join(self.parts)

    @property
    def python(self) -> str:
        return self.abi

    @property
    def abi(self) -> str:
        return self._parts[0]

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and other.parts == self.parts

    def __hash__(self) -> int:
        return hash(str(self))
