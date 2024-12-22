<h1 align="center">ihook</h1>

<div align="center">

[![codecov](https://codecov.io/github/JezaChen/ihook/graph/badge.svg?token=DN5JNB0KIK)](https://codecov.io/github/JezaChen/ihook)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ihook?style=flat-square)
![GitHub](https://img.shields.io/github/license/jezachen/ihook)

</div>

`ihook` is a Python module that allows you to configure functions to call when importing modules.
It supports both case-sensitive and case-insensitive module names and can handle hooks for modules that are imported using methods of  `importlib`.

## Features

- Hook for modules that are imported.
- Support for case-sensitive and case-insensitive module names.
- Chain multiple hooks for the same or different modules.
- Handle hooks for sub-packages and namespace packages.

## Installation

You can install `ihook` using `pip`:

```sh
pip install ihook
```

## Usage

### Registering Hooks

You can register hooks using the `@on_import` decorator or by calling the `on_import` function directly.

#### Using the Decorator

```python
import ihook

@ihook.on_import('math')
def on_math_import():
    print('math module imported')

import math  # This will trigger the hook and print 'math module imported'
```

#### Using the Function Directly

```python
import ihook

def on_socket_import():
    print('socket module imported')

ihook.on_import('socket', on_socket_import)

import socket  # This will trigger the hook and print 'socket module imported'
```

### Case-Insensitive Hooks

You can register hooks for module names in a case-insensitive manner by setting the `case_sensitive` parameter to `False`.

```python
import ihook

@ihook.on_import('SocKet', case_sensitive=False)
def on_socket_import():
    print('socket module imported (case-insensitive)')

import socket  # This will trigger the hook and print 'socket module imported (case-insensitive)'
```

### Hooks with Module Information

You can define hooks that take a `ModuleInfo` parameter, which provides more detailed information about the imported module.
You can handle direct access to the module object using the `module_object` attribute.

```python
import ihook

@ihook.on_import('socket')
def on_socket_import(module_info: ihook.ModuleInfo):
    print(f'{module_info.module_name} module imported')
    print(f'Module object: {module_info.module_object}')

import socket  # This will trigger the hook and print module information
```

### Clearing Hooks

You can clear all registered hooks using the `clear_hooks` function.

```python
import ihook

ihook.clear_hooks()  # This will clear all registered hooks
```

## Advanced Usage

### Handling Importlib

You can register hooks for modules that are imported or reloaded using `importlib`.

```python
import ihook

@ihook.on_import('hashlib')
def on_hashlib_import():
    print('hashlib module imported')

import importlib
hashlib = importlib.import_module('hashlib')  # This will trigger the hook and print 'hashlib module imported'
importlib.reload(hashlib)  # This will trigger the hook again and print 'hashlib module imported'
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
