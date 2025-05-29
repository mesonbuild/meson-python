# Contributing

Thank you for your interest in contributing to `meson-python`!

## How to Contribute

1. **Fork the repository** and create your branch from `main`.
2. **Install Ninja** either using your system package manager (preferred) or via `pip install ninja`.
3. **Setup development environment** using `pip install -e .[test]`.
   This will install as well all necessary dependencies for development and testing.

   It is recommended to use a virtual environment to avoid conflicts with system packages.
5. **Make your changes** and add tests if applicable.
6. **Run the test suite** to ensure all tests pass: `pytest` from the project root.
7. **Submit a pull request** with a clear description of your changes.

## Code Style
- Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide, but with a line length of 127 characters.
- Use Ruff for linting.
