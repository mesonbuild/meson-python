# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import io
import os
import pathlib
import pkgutil
import re
import subprocess
import sys

from contextlib import redirect_stdout

import pytest

import mesonpy

from mesonpy import _editable

from .test_wheel import EXT_SUFFIX, NOGIL_BUILD


def find_cython_version():
    cython_version_str = subprocess.run(['cython', '--version'], check=True,
                                        stdout=subprocess.PIPE, text=True).stdout
    version_str = re.search(r'(\d{1,4}\.\d{1,4}\.?\d{0,4})', cython_version_str).group(0)
    return tuple(map(int, version_str.split('.')))

CYTHON_VERSION = find_cython_version()


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


@pytest.mark.skipif(NOGIL_BUILD and CYTHON_VERSION < (3, 1, 0),
                    reason='Cython version too old, no free-threaded CPython support')
def test_mesonpy_meta_finder(package_complex, tmp_path):
    # build a package in a temporary directory
    project = mesonpy.Project(package_complex, tmp_path)

    # point the meta finder to the build directory
    finder = _editable.MesonpyMetaFinder('complex', {'complex'}, os.fspath(tmp_path), project._build_command, True)

    # check repr
    assert repr(finder) == f'MesonpyMetaFinder(\'complex\', {str(tmp_path)!r})'

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
        import complex.extension
        assert complex.extension.__spec__.origin == os.fspath(tmp_path / f'extension{EXT_SUFFIX}')
        assert complex.extension.answer() == 42
        import complex.namespace.foo
        assert complex.namespace.foo.__spec__.origin == os.fspath(package_complex / 'complex/namespace/foo.py')
        assert complex.namespace.foo.foo() == 'foo'
    finally:
        # remove finder from the meta path
        del sys.meta_path[0]


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
    project = mesonpy.Project(package_path, tmp_path)

    # point the meta finder to the build directory
    finder = _editable.MesonpyMetaFinder('simple', {'simple'}, os.fspath(tmp_path), project._build_command, True)

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
    project = mesonpy.Project(package_path, tmp_path)

    # point the meta finder to the build directory
    finder = _editable.MesonpyMetaFinder('simple', {'simple'}, os.fspath(tmp_path), project._build_command, True)

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


@pytest.mark.skipif(NOGIL_BUILD and CYTHON_VERSION < (3, 1, 0),
                    reason='Cython version too old, no free-threaded CPython support')
def test_editable_pkgutils_walk_packages(package_complex, tmp_path):
    # build a package in a temporary directory
    project = mesonpy.Project(package_complex, tmp_path)

    finder = _editable.MesonpyMetaFinder('complex', {'complex'}, os.fspath(tmp_path), project._build_command, True)

    try:
        # install editable hooks
        sys.meta_path.insert(0, finder)
        sys.path_hooks.insert(0, finder._path_hook)

        import complex
        packages = {m.name for m in pkgutil.walk_packages(complex.__path__, complex.__name__ + '.')}
        assert packages == {
            'complex.bar',
            'complex.extension',
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
    project = mesonpy.Project(package_custom_target_dir, tmp_path)
    finder = _editable.MesonpyMetaFinder('package', {'package'}, os.fspath(tmp_path), project._build_command, True)
    try:
        sys.meta_path.insert(0, finder)
        import package.generated.one
        import package.generated.two  # noqa: F401
    finally:
        del sys.meta_path[0]


@pytest.mark.parametrize('verbose', [False, True], ids=('', 'verbose'))
@pytest.mark.parametrize('args', [[], ['-j1']], ids=('', '-Ccompile-args=-j1'))
def test_editable_rebuild(package_purelib_and_platlib, tmp_path, verbose, args):
    with mesonpy._project({'builddir': os.fspath(tmp_path), 'compile-args': args}) as project:

        finder = _editable.MesonpyMetaFinder(
            project._metadata.name, {'plat', 'pure'},
            os.fspath(tmp_path), project._build_command,
            verbose=verbose,
        )

        try:
            # Install editable hooks
            sys.meta_path.insert(0, finder)

            # Import module and trigger rebuild. Importing any module in the
            # Python package triggers the build. Use the the pure Python one as
            # Cygwin is not happy when reloading an extension module.
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                import pure
            assert not verbose or stdout.getvalue().startswith('meson-python: building ')

            # Reset state.
            del sys.modules['pure']
            finder._rebuild.cache_clear()

            # Importing again should result in no output.
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                import pure  # noqa: F401
            assert stdout.getvalue() == ''

        finally:
            del sys.meta_path[0]
            sys.modules.pop('pure', None)


@pytest.mark.skipif(NOGIL_BUILD and CYTHON_VERSION < (3, 1, 0),
                    reason='Cython version too old, no free-threaded CPython support')
def test_editable_verbose(venv, package_complex, editable_complex, monkeypatch):
    monkeypatch.setenv('MESONPY_EDITABLE_VERBOSE', '1')
    venv.pip('install', os.fspath(editable_complex))

    # Importing the module should not result in any output since the project has already been built
    assert venv.python('-c', 'import complex').strip() == ''

    # Touch a compiled source file and make sure that the build info is output on import
    package_complex.joinpath('test.pyx').touch()
    output = venv.python('-c', 'import complex').strip()
    assert output.startswith('meson-python: building complex: ')

    # Another import without file changes should not show any output
    assert venv.python('-c', 'import complex') == ''


@pytest.mark.parametrize('verbose', [False, True], ids=('', 'verbose'))
def test_editable_rebuild_error(package_purelib_and_platlib, tmp_path, verbose):
    with mesonpy._project({'builddir': os.fspath(tmp_path)}) as project:

        finder = _editable.MesonpyMetaFinder(
            project._metadata.name, {'plat', 'pure'},
            os.fspath(tmp_path), project._build_command,
            verbose=verbose,
        )
        path = package_purelib_and_platlib / 'plat.c'
        code = path.read_text()

        try:
            # Install editable hooks
            sys.meta_path.insert(0, finder)

            # Insert invalid code in the extension module source code
            path.write_text('return')

            # Import module and trigger rebuild: the build fails and ImportErrror is raised
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                with pytest.raises(ImportError, match='re-building the purelib-and-platlib '):
                    import plat  # noqa: F401
            assert not verbose or stdout.getvalue().startswith('meson-python: building ')

        finally:
            del sys.meta_path[0]
            sys.modules.pop('pure', None)
            path.write_text(code)
