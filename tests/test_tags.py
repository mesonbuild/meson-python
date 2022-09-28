# SPDX-License-Identifier: MIT

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
        ('cp311-win_amd64', 'cpython', '311', ('win_amd64', ), 'cp311', 'cp311'),
        ('cpython-311-win_amd64', 'cpython', '311', ('win_amd64', ), 'cp311', 'cp311'),
        ('cpython-310-special', 'cpython', '310', ('special',), 'cp310', 'cp310'),
        ('cpython-310-x86_64-linux-gnu', 'cpython', '310', ('x86_64', 'linux', 'gnu'), 'cp310', 'cp310'),
        ('pypy39-pp73-x86_64-linux-gnu', 'pypy39', 'pp73', ('x86_64', 'linux', 'gnu'), 'pypy39_pp73', 'pp39'),
        ('pypy39-pp73-win_amd64', 'pypy39', 'pp73', ('win_amd64', ), 'pypy39_pp73', 'pp39'),
        ('pypy38-pp73-darwin', 'pypy38', 'pp73', ('darwin', ), 'pypy38_pp73', 'pp38'),
    ]
)
def test_interpreter_tag(value, implementation, version, additional, abi, python):
    tag = mesonpy._tags.InterpreterTag(value)
    if not value.startswith('cp311'):
        # Avoid testing the workaround for the invalid Windows tag
        assert str(tag) == value

    assert tag.implementation == implementation
    assert tag.interpreter_version == version
    assert tag.additional_information == additional
    assert tag.abi == abi
    assert tag.python == python
    assert tag == mesonpy._tags.InterpreterTag(value)


@pytest.mark.parametrize(
    ('value', 'msg'),
    [
        ('', 'Invalid PEP 3149 interpreter tag, expected at least 2 parts but got 1'),
        ('invalid', 'Invalid PEP 3149 interpreter tag, expected at least 2 parts but got 1'),
    ]
)
def test_interpreter_tag_invalid(value, msg):
    with pytest.raises(ValueError, match=msg):
        mesonpy._tags.InterpreterTag(value)
