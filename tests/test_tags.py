# SPDX-License-Identifier: EUPL-1.2

import re
import sys

import pytest

import mesonpy._tags


INTERPRETER_VERSION = f'{sys.version_info[0]}{sys.version_info[1]}'


@pytest.mark.parametrize(
    ('value', 'number', 'abi', 'python'),
    [
        ('abi3', 3, 'abi3', None),
        ('abi4', 4, 'abi4', None),
    ]
)
def test_stable_abi_tag(value, number, abi, python):
    tag = mesonpy._tags.StableABITag(value)
    assert str(tag) == value
    assert tag.abi_number == number
    assert tag.abi == abi
    assert tag.python == python
    assert tag == mesonpy._tags.StableABITag(value)


def test_stable_abi_tag_invalid():
    with pytest.raises(ValueError, match=re.escape(
        r'Invalid PEP 3149 stable ABI tag, expecting pattern `^abi(?P<abi_number>[0-9]+)$`'
    )):
        mesonpy._tags.StableABITag('invalid')


@pytest.mark.parametrize(
    ('value', 'implementation', 'version', 'additional', 'abi', 'python'),
    [
        ('cpython-37-x86_64-linux-gnu', 'cpython', '37', ('x86_64', 'linux', 'gnu'), 'cp37', 'cp37'),
        ('cpython-310-x86_64-linux-gnu', 'cpython', '310', ('x86_64', 'linux', 'gnu'), 'cp310', 'cp310'),
        ('cpython-310', 'cpython', '310', (), 'cp310', 'cp310'),
        ('cpython-310-special', 'cpython', '310', ('special',), 'cp310', 'cp310'),
        ('pypy-41', 'pypy', '41', (), 'pypy_41', f'pp{INTERPRETER_VERSION}'),
        ('pypy3-72-x86_64-linux-gnu', 'pypy3', '72', ('x86_64', 'linux', 'gnu'), 'pypy3_72', f'pp{INTERPRETER_VERSION}'),
        ('cpython-310-x86_64-linux-gnu', 'cpython', '310', ('x86_64', 'linux', 'gnu'), 'cp310', 'cp310'),
    ]
)
def test_linux_interpreter_tag(value, implementation, version, additional, abi, python):
    tag = mesonpy._tags.LinuxInterpreterTag(value)
    assert str(tag) == value
    assert tag.implementation == implementation
    assert tag.interpreter_version == version
    assert tag.additional_information == additional
    assert tag.abi == abi
    assert tag.python == python
    assert tag == mesonpy._tags.LinuxInterpreterTag(value)


@pytest.mark.parametrize(
    ('value', 'msg'),
    [
        ('', 'Invalid PEP 3149 interpreter tag, expected at least 2 parts but got 1'),
        ('invalid', 'Invalid PEP 3149 interpreter tag, expected at least 2 parts but got 1'),
    ]
)
def test_linux_interpreter_tag_invalid(value, msg):
    with pytest.raises(ValueError, match=msg):
        mesonpy._tags.LinuxInterpreterTag(value)


@pytest.mark.parametrize(
    ('value', 'parts', 'abi', 'python'),
    [
        ('cp310-win_amd64', ('cp310', 'win_amd64'), 'cp310', 'cp310'),
        ('cp38-win32', ('cp38', 'win32'), 'cp38', 'cp38')
    ]
)
def test_windows_interpreter_tag(value, parts, abi, python):
    tag = mesonpy._tags.WindowsInterpreterTag(value)
    assert str(tag) == value
    assert tag.parts == parts
    assert tag.abi == abi
    assert tag.python == python
    assert tag == mesonpy._tags.WindowsInterpreterTag(value)


@pytest.mark.parametrize('value', ['', 'unknown', 'too-much-information'])
def test_windows_interpreter_tag_warn(value):
    with pytest.warns(Warning, match=(
        'Unexpected native module tag name, the ABI dectection might be broken. '
        'Please report this to https://github.com/FFY00/mesonpy/issues '
        'and include information about the Python distribution you are using.'
    )):
        mesonpy._tags.WindowsInterpreterTag(value)
