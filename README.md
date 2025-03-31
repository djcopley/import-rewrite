# Python Import Rewriter

A flexible library for dynamically rewriting Python imports at runtime using metapath hooks.

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Tests](https://github.com/djcopley/import-rewriter/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/djcopley/import-rewriter/actions/workflows/tests.yml)
[![PyPI version](https://badge.fury.io/py/import-rewriter.svg)](https://badge.fury.io/py/import-rewriter)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/import-rewriter.svg)](https://pypi.python.org/pypi/import-rewriter/)
[![Downloads](https://static.pepy.tech/badge/import-rewriter)](https://pepy.tech/project/import-rewriter)

## Overview

Import Rewriter allows you to transparently redirect imports in Python code without modifying the source. This is useful for:

- Providing mock implementations during testing
- Implementing feature toggles or A/B testing at the module level
- Creating compatibility layers for different library versions
- Redirecting imports for dependency injection
- Implementing module aliases for refactoring
- Vendoring dependencies at runtime

The library works by intercepting the Python import system using metapath hooks and rewriting the import statements in the Abstract Syntax Tree (AST) before execution.

## Installation

```bash
pip install import-rewriter
```

## Quick Start

```python
from import_rewriter import install_import_rewriter

# Redirect imports of 'legacy_module' to use 'modern_module' instead
install_import_rewriter({
    'legacy_module': 'modern_module',
    'requests': 'my_custom_requests'
})

# Now when your code does:
import legacy_module
# It will actually import 'modern_module'
```

## Features

- Transparently rewrites imports without changing the original code
- Handles both `import x` and `from x import y` statements
- Can be enabled/disabled at runtime
- Minimal performance impact for non-rewritten imports
- Works with standard Python imports, no special syntax required
- Preserves import aliases (`import x as y`)

## API Reference

### `install_import_rewriter(import_map=None)`

Installs the import rewriting hook with the specified mapping.

**Parameters:**
- `import_map` (dict): A dictionary mapping original import names to replacement names.

**Returns:**
- The finder instance that was installed (can be used to uninstall later).

**Example:**
```python
finder = install_import_rewriter({
    'pandas': 'custom_pandas',
    'tensorflow': 'tensorflow_lite'
})
```

### Uninstalling the Hook

To remove the hook and restore normal import behavior:

```python
import sys
sys.meta_path.remove(finder)
```

## Advanced Usage

### Selective Module Rewriting

You can selectively rewrite imports for specific modules or packages:

```python
install_import_rewriter({
    'pandas.DataFrame': 'my_package.DataFrame',
    'numpy.array': 'my_package.fast_array'
})
```

### Dynamic Rewriting

You can change the import mapping at runtime:

```python
finder = install_import_rewriter()
finder.import_map['requests'] = 'mock_requests'  # Add new mapping
```

## How It Works

Import Rewriter uses three key components:

1. **MetaPath Finder**: Intercepts import requests before they're processed by the standard import machinery.
2. **AST Transformer**: Parses and modifies the abstract syntax tree of the source code.
3. **Custom Loader**: Executes the modified code in the module's namespace.

When a module is imported, the finder intercepts the request, the transformer rewrites any matching imports, and the loader executes the modified code.

## Limitations

- Only rewrites imports in modules that are loaded after the hook is installed
- Cannot rewrite imports in c-extensions, built-in, or frozen modules
- May have unpredictable interactions with other import hooks

## License

GPLv3

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
