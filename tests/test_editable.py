# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import functools
import os
import pathlib
import pkgutil
import sys

import pytest

import mesonpy

from mesonpy import _editable

from .test_wheel import EXT_SUFFIX, tag


def test_walk(package_complex):
    entries = _editable.walk(
        os.fspath(package_complex / 'complex'),
        [os.path.normpath('more/meson.build'), os.path.normpath('more/baz.pyx')],
        [os.path.normpath('namespace')],
    )
    assert {pathlib.Path(x) for x in entries} == {
        pathlib.Path('__init__.py'),
        pathlib.Path('more/__init__.py'),
    }


def test_nodes_tree():
    tree = _editable.Node()
    tree[('aa', 'bb', 'cc')] = 'path1'
    tree[('aa', 'dd')] = 'path2'
    assert tree['aa']['bb']['cc'] == 'path1'
    assert tree['aa']['dd'] == 'path2'
    assert tree[('aa', 'bb', 'cc')] == 'path1'
    assert tree.get(('aa', 'bb', 'cc')) == 'path1'
    assert tree['aa'] == tree[('aa', )]
    assert tree.get(('aa', 'gg')) is None
    assert tree[('aa', 'gg')] == _editable.Node()


def test_collect(package_complex):
    root = os.fspath(package_complex)
    install_plan = {
        'targets': {
            os.path.join(root, 'build', f'test{EXT_SUFFIX}'): {
                'destination': os.path.join('{py_platlib}', 'complex', f'test{EXT_SUFFIX}'),
                'tag': 'runtime'},
        },
        'install_subdirs': {
            os.path.join(root, 'complex'): {
                'destination': os.path.join('{py_platlib}', 'complex'),
                'tag': None}
        }
    }
    tree = _editable.collect(install_plan)
    assert tree['complex']['__init__.py'] == os.path.join(root, 'complex', '__init__.py')
    assert tree['complex'][f'test{EXT_SUFFIX}'] == os.path.join(root, 'build', f'test{EXT_SUFFIX}')
    assert tree['complex']['more']['__init__.py'] == os.path.join(root, 'complex', 'more', '__init__.py')


@pytest.mark.parametrize(
    'make_finder',
    [_editable.MesonpyMetaFinder, functools.partial(_editable.MesonpyMetaFinder, verbose=True)]
)
def test_mesonpy_meta_finder(package_complex, tmp_path, make_finder):
    # build a package in a temporary directory
    mesonpy.Project(package_complex, tmp_path)

    # point the meta finder to the build directory
    build_cmd = ['meson', 'compile'] if sys.platform == 'win32' else ['ninja']
    finder = make_finder({'complex'}, os.fspath(tmp_path), build_cmd)

    # check repr
    assert repr(finder) == f'MesonpyMetaFinder({str(tmp_path)!r})'

    # verify that we can look up a pure module in the source directory
    spec = finder.find_spec('complex')
    assert spec.name == 'complex'
    assert isinstance(spec.loader, _editable.SourceFileLoader)
    assert spec.origin == os.fspath(package_complex / 'complex/__init__.py')

    # and an extension module in the build directory
    spec = finder.find_spec('complex.test')
    assert spec.name == 'complex.test'
    assert isinstance(spec.loader, _editable.ExtensionFileLoader)
    assert spec.origin == os.fspath(tmp_path / f'test{EXT_SUFFIX}')

    try:
        # install the finder in the meta path
        sys.meta_path.insert(0, finder)
        # verify that we can import the modules
        import complex
        assert complex.__spec__.origin == os.fspath(package_complex / 'complex/__init__.py')
        assert complex.__file__ == os.fspath(package_complex / 'complex/__init__.py')
        import complex.test
        assert complex.test.__spec__.origin == os.fspath(tmp_path / f'test{EXT_SUFFIX}')
        assert complex.test.answer() == 42
        import complex.namespace.foo
        assert complex.namespace.foo.__spec__.origin == os.fspath(package_complex / 'complex/namespace/foo.py')
        assert complex.namespace.foo.foo() == 'foo'
    finally:
        # remove finder from the meta path
        del sys.meta_path[0]
        # unload complex module and all its submodules to be able to run parametrized tests without side-effects
        for module in ['complex', 'complex.test', 'complex.namespace', 'complex.namespace.foo']:
            sys.modules.pop(module, None)


def test_mesonpy_traversable():
    tree = _editable.Node()
    tree[('package', '__init__.py')] = '/tmp/src/package/__init__.py'
    tree[('package', 'src.py')] = '/tmp/src/package/src.py'
    tree[('package', 'data.txt')] = '/tmp/src/package/data.txt'
    tree[('package', 'nested', '__init__.py')] = '/tmp/src/package/nested/__init__.py'
    tree[('package', 'nested', 'some.py')] = '/tmp/src/package/nested/some.py'
    tree[('package', 'nested', 'generated.txt')] = '/tmp/build/generated.txt'
    traversable = _editable.MesonpyTraversable('package', tree['package'])
    assert {x.name for x in traversable.iterdir()} == {'__init__.py', 'src.py', 'data.txt', 'nested'}
    nested = traversable / 'nested'
    assert nested.is_dir()
    assert {x.name for x in nested.iterdir()} == {'__init__.py', 'some.py', 'generated.txt'}
    generated = traversable.joinpath('nested', 'generated.txt')
    assert isinstance(generated, pathlib.Path)
    assert generated == pathlib.Path('/tmp/build/generated.txt')
    bad = traversable / 'bad'
    assert not bad.is_file()
    assert not bad.is_dir()
    with pytest.raises(FileNotFoundError):
        bad.open()


def test_resources(tmp_path):
    # build a package in a temporary directory
    package_path = pathlib.Path(__file__).parent / 'packages' / 'simple'
    mesonpy.Project(package_path, tmp_path)

    # point the meta finder to the build directory
    finder = _editable.MesonpyMetaFinder({'simple'}, os.fspath(tmp_path), ['ninja'])

    # verify that we can look up resources
    spec = finder.find_spec('simple')
    reader = spec.loader.get_resource_reader('simple')
    traversable = reader.files()
    assert {x.name for x in traversable.iterdir()} == {'__init__.py', 'test.py', 'data.txt'}
    with traversable.joinpath('data.txt').open() as f:
        text = f.read().rstrip()
    assert text == 'ABC'


@pytest.mark.skipif(sys.version_info < (3, 9), reason='importlib.resources not available')
def test_importlib_resources(tmp_path):
    # build a package in a temporary directory
    package_path = pathlib.Path(__file__).parent / 'packages' / 'simple'
    mesonpy.Project(package_path, tmp_path)

    # point the meta finder to the build directory
    finder = _editable.MesonpyMetaFinder({'simple'}, os.fspath(tmp_path), ['ninja'])

    try:
        # install the finder in the meta path
        sys.meta_path.insert(0, finder)
        # verify that we can import the modules
        import simple
        assert simple.__spec__.origin == os.fspath(package_path / '__init__.py')
        assert simple.__file__ == os.fspath(package_path / '__init__.py')
        assert simple.data() == 'ABC'
        # load resources via importlib
        import importlib.resources
        with importlib.resources.files(simple).joinpath('data.txt').open() as f:
            text = f.read().rstrip()
        assert text == 'ABC'
        assert importlib.resources.files(simple).joinpath('data.txt').read_text().rstrip() == 'ABC'
    finally:
        # remove finder from the meta path
        del sys.meta_path[0]


def test_editable_install(venv, editable_simple):
    venv.pip('install', os.fspath(editable_simple))
    assert venv.python('-c', 'import simple; print(simple.data())').strip() == 'ABC'


def test_editble_reentrant(venv, editable_imports_itself_during_build):
    venv.pip('install', os.fspath(editable_imports_itself_during_build))
    assert venv.python('-c', 'import plat; print(plat.data())').strip() == 'ABC'

    path = pathlib.Path(__file__).parent / 'packages' / 'imports-itself-during-build' / 'plat.c'
    code = path.read_text()

    try:
        # edit souce code
        path.write_text(code.replace('ABC', 'DEF'))
        # check that the module is rebuilt on import. the build proess
        # imports python code from the source directory, thus this
        # test also check that this import does not cause an rebuild
        # loop
        assert venv.python('-c', 'import plat; print(plat.data())').strip() == 'DEF'
    finally:
        path.write_text(code)


@pytest.mark.skipif(tag.platform.startswith('musllinux'), reason='ninja -n segfaults on Alpine container')
def test_editable_verbose(venv, editable_complex, monkeypatch):
    monkeypatch.setenv(_editable.VERBOSE, '1')
    venv.pip('install', os.fspath(editable_complex))

    # First import to make sure that the project is built
    venv.python('-c', 'import complex')

    # Second import should have no output since the project has already been built
    assert venv.python('-c', 'import complex').strip() == ''

    # Touch the pyx and make sure that the building info is seen
    complex_package_dir = venv.python(
        '-c', 'import os; import complex; print(os.path.dirname(complex.__file__))').strip()
    cython_path = pathlib.Path(complex_package_dir).parent / 'test.pyx'
    cython_path.touch()
    output = venv.python('-c', 'import complex').strip()
    assert output.startswith('meson-python: building complex with')

    # Another import without file changes should not show any output
    assert venv.python('-c', 'import complex') == ''


def test_editable_pkgutils_walk_packages(package_complex, tmp_path):
    # build a package in a temporary directory
    mesonpy.Project(package_complex, tmp_path)

    finder = _editable.MesonpyMetaFinder({'complex'}, os.fspath(tmp_path), ['ninja'])

    try:
        # install editable hooks
        sys.meta_path.insert(0, finder)
        sys.path_hooks.insert(0, finder._path_hook)

        import complex
        packages = {m.name for m in pkgutil.walk_packages(complex.__path__, complex.__name__ + '.')}
        assert packages == {
            'complex.bar',
            'complex.more',
            'complex.more.baz',
            'complex.more.move',
            'complex.test',
        }

        from complex import namespace
        packages = {m.name for m in pkgutil.walk_packages(namespace.__path__, namespace.__name__ + '.')}
        assert packages == {
            'complex.namespace.bar',
            'complex.namespace.foo',
        }

    finally:
        # remove hooks
        del sys.meta_path[0]
        del sys.path_hooks[0]


def test_custom_target_install_dir(package_custom_target_dir, tmp_path):
    mesonpy.Project(package_custom_target_dir, tmp_path)
    finder = _editable.MesonpyMetaFinder({'package'}, os.fspath(tmp_path), ['ninja'])
    try:
        sys.meta_path.insert(0, finder)
        import package.generated.one
        import package.generated.two  # noqa: F401
    finally:
        del sys.meta_path[0]
