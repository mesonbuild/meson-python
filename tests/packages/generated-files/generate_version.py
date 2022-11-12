import argparse
import os


def write_version_info(path):
    # A real project would call something to generate this
    dummy_version = '1.0.0'
    dummy_hash = '013j2fiejqea'
    if os.environ.get('MESON_DIST_ROOT'):
        path = os.path.join(os.environ.get('MESON_DIST_ROOT'), path)
    with open(path, 'w') as file:
        file.write(f'__version__="{dummy_version}"\n')
        file.write(
            f'__git_version__="{dummy_hash}"\n'
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--outfile', type=str, help='Path to write version info to'
    )
    args = parser.parse_args()

    if not args.outfile.endswith('.py'):
        raise ValueError(
            f'Output file must be a Python file. '
            f'Got: {args.outfile} as filename instead'
        )

    write_version_info(args.outfile)


main()
