
# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import abc
import dataclasses
import difflib
import functools
import itertools
import pathlib
import typing

import pyproject_metadata

import mesonpy._util

from mesonpy._compat import Mapping


if typing.TYPE_CHECKING:
    from typing import Any, Callable

    from mesonpy._compat import Collection, Iterator, Sequence



class DataFetcher(pyproject_metadata.DataFetcher):  # type: ignore[misc]
    """Custom data fetcher that provides a key mapping functionality."""
    def __init__(self, data: Mapping[str, Any], key_map: Callable[[str],  str] | None = None) -> None:
        super().__init__(data)
        self._key_map = key_map

    def get(self, key: str) -> Any:
        if self._key_map:
            key = self._key_map(key)
        val = super().get(key)
        # XXX: convert tuples to lists because get_list currently does  not accept tuples
        if isinstance(val, tuple):
            return list(val)
        return val


@dataclasses.dataclass
class MesonArgs:
    """Data class that holds the user configurable Meson arguments settings."""
    dist: list[str] = dataclasses.field(default_factory=list)
    setup: list[str] = dataclasses.field(default_factory=list)
    compile: list[str] = dataclasses.field(default_factory=list)
    install: list[str] = dataclasses.field(default_factory=list)

    def __add__(self, other: Any) -> MesonArgs:
        if not isinstance(other, self.__class__):
            raise TypeError(f'Invalid type: {type(other)}')
        return self.__class__(
            self.dist + other.dist,
            self.setup + other.setup,
            self.compile + other.compile,
            self.install + other.install,
        )

    @classmethod
    def from_fetcher(cls, fetcher: pyproject_metadata.DataFetcher) -> MesonArgs:
        """Create an instance from a data fetcher object."""
        return cls(
            fetcher.get_list('dist'),
            fetcher.get_list('setup'),
            fetcher.get_list('compile'),
            fetcher.get_list('install'),
        )


class StrictSettings(abc.ABC):
    """Helper class that provides unknown keys checks."""

    @classmethod
    def _get_key(cls, data: Mapping[Any, Any], key: str) -> Mapping[Any, Any]:
        try:
            for part in key.split('.'):
                data = data[part]
        except  KeyError:
            return {}
        return data

    @classmethod
    @functools.lru_cache(maxsize=None)
    def _expected_keys(cls) -> Collection[str]:
        """Calculates an expanded list of all the possible expected key.

        Eg. If we had the 'a.b.c.d.e.f' and 'a.b.c.xxx' keys, it would generate
            'a', 'a.b', 'a.b.c', 'a.b.c.d', 'a.b.c.xxx', 'a.b.c.d.e', and 'a.b.c.d.e.f'.
        """
        def join(*args: str) -> str:
            return '.'.join(args)

        return frozenset(itertools.chain.from_iterable(
            itertools.accumulate(key.split('.'), join)
            for key in cls.valid_keys()
        ))

    @classmethod
    @functools.lru_cache(maxsize=None)
    def _valid_keys(cls) -> Collection[str]:
        """Caches the valid_keys() method implemented by the children."""
        return frozenset(cls.valid_keys())

    @classmethod
    def _unexpected_keys(cls, data: Any, key: str = '') -> Iterator[tuple[str, Sequence[str]]]:
        """Iterates over the unexpected keys in a data object."""
        if key and key not in cls._expected_keys():
            yield key, sorted(difflib.get_close_matches(key, cls._valid_keys(), n=3))
        elif isinstance(data, Mapping):
            for name, value in data.items():
                yield from cls._unexpected_keys(value, f'{key}.{name}' if key else name)

    @classmethod
    def check_for_unexpected_keys(cls, data: Mapping[Any, Any], active_prefix: str = '') -> None:
        """Checks if there are any unexpected keys in a data object."""
        if active_prefix:
            data = cls._get_key(data, active_prefix)
        unknown = list(cls._unexpected_keys(data, active_prefix))
        if not unknown:
            return
        error_msg = 'The following unknown configuration entries were found:\n'
        for key, matches in unknown:
            error_msg += f'\t- {key}'
            if matches:
                match_list = mesonpy._util.natural_language_list(matches, conjunction='or')
                error_msg += f' (did you mean {match_list}?)'
            error_msg += '\n'
        raise pyproject_metadata.ConfigurationError(error_msg)

    @classmethod
    @abc.abstractmethod
    def valid_keys(cls) -> Iterator[str]:
        """Provides a list of all valid keys."""


@dataclasses.dataclass
class BuildHookSettings(StrictSettings):
    """build_wheel hook config_settings."""
    builddir: pathlib.Path | None = None
    meson_args: MesonArgs = dataclasses.field(default_factory=MesonArgs)
    editable_verbose: bool = False

    @classmethod
    def _key_map(cls, key: str) -> str:
        return key.replace('_', '-')

    @classmethod
    def _meson_args_key_map(cls, key: str) -> str:
        return f'{key}-args'

    @classmethod
    def valid_keys(cls) -> Iterator[str]:
        for field in dataclasses.fields(cls):
            if field.name == 'meson_args':
                continue
            yield cls._key_map(field.name)
        for field in dataclasses.fields(MesonArgs):
            yield cls._meson_args_key_map(field.name)

    @classmethod
    def from_config_settings(cls, data: Mapping[str, Any]) -> BuildHookSettings:
        cls.check_for_unexpected_keys(data)

        fetcher = DataFetcher(data)
        try:
            builddir = fetcher.get('builddir')
        except KeyError:
            builddir = None
        if isinstance(builddir, list):
            if len(builddir) >= 2:
                raise pyproject_metadata.ConfigurationError(
                    'Only one value for configuration entry "builddir" can be specified'
                )
            builddir = builddir[0]
        if builddir is not None and not isinstance(builddir, str):
            raise pyproject_metadata.ConfigurationError(
                'Configuration entry "builddir" has an invalid type, '
                f'expecting a string (got "{builddir}")'
            )

        return cls(
            pathlib.Path(builddir) if builddir else None,
            MesonArgs.from_fetcher(DataFetcher(data, cls._meson_args_key_map)),
            bool(fetcher.get_str('editable-verbose')),
        )


@dataclasses.dataclass
class ToolSettings(StrictSettings):
    """pyproject.toml settings."""
    meson_args: MesonArgs

    @classmethod
    def _meson_args_key_map(cls, key: str) -> str:
        return f'tool.meson-python.args.{key}'

    @classmethod
    def valid_keys(cls) -> Iterator[str]:
        for field in dataclasses.fields(MesonArgs):
            yield cls._meson_args_key_map(field.name)

    @classmethod
    def from_pyproject(cls, data: Mapping[str, Any]) -> ToolSettings:
        cls.check_for_unexpected_keys(data, 'tool.meson-python')

        return cls(
            MesonArgs.from_fetcher(DataFetcher(data, cls._meson_args_key_map)),
        )
