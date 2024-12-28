import enum
import types
from collections import defaultdict
import functools
import typing
import sys
import inspect

# todo: unpatch support for previously patched modules to prevent further hooks
# todo: unit tests to improve custom loader

__all__ = [
    # types
    'ModuleInfo',

    # enums
    'PatchMethods',

    # functions
    'on_import',
    'clear_hooks',
    'current_patch_method',

    # type hints
    'CALLBACK_FUNC_WITH_NO_PARAMS',
    'CALLBACK_FUNC_WITH_MODULE_INFO_PARAM',
    'HOOK_CALLBACK_FUNC',
]

_HOOKED_MARK = '__hooked__'


class PatchMethods(enum.Enum):
    """ The patch methods.

    Now, we only support `PATCH_META_PATH`, where we patch the `sys.meta_path`.
    """
    PATCH_META_PATH = enum.auto()


_PATCH_METHOD = PatchMethods.PATCH_META_PATH


def _get_module_name(module: types.ModuleType) -> str:
    """ Get the module name from the module object.

    :note:
        - If the module has `__spec__` attribute, then use `__spec__.name`.
        - Otherwise, use `__name__`.

        If a module is run as a script by using the `-m` flag,
        the `module.__spec__.name` will reflect the actual module name while `module.__name__` will be `__main__`.

        See PEP-451 for more details: https://www.python.org/dev/peps/pep-0451/
    """
    try:
        return module.__spec__.name
    except AttributeError:
        return module.__name__


class ModuleInfo:
    # === Type hints ===
    module_object: types.ModuleType
    module_name: str

    # === Slots ===
    __slots__ = ['module_object', 'module_name']

    def __init__(self, module_object: types.ModuleType, module_name: str):
        self.module_object = module_object
        self.module_name = module_name

    def __iter__(self):
        """ Convenient method to unpack the module info. """
        return iter((self.module_object, self.module_name))

    @classmethod
    def from_module(cls, module: types.ModuleType):
        """ Create a `ModuleInfo` object from the module object. """
        return cls(module, _get_module_name(module))


# === Type hints for callback functions ===
# The callback functions can have two types:
#   - No parameters
#   - One parameter of type `ModuleInfo`, which contains the module object and the module name.
CALLBACK_FUNC_WITH_NO_PARAMS = typing.Callable[[], None]
CALLBACK_FUNC_WITH_MODULE_INFO_PARAM = typing.Callable[[ModuleInfo], None]

HOOK_CALLBACK_FUNC = typing.Union[
    CALLBACK_FUNC_WITH_NO_PARAMS,
    CALLBACK_FUNC_WITH_MODULE_INFO_PARAM,
]


def _call_helper(func: HOOK_CALLBACK_FUNC, module: types.ModuleType):
    """
    A helper function to call the callback function with the appropriate parameters.
        - func(ModuleInfo) if the callback function takes one parameter
        - func() if the callback function takes no parameters
    """
    sig = inspect.signature(func)
    if len(sig.parameters) == 0:
        func()
    elif len(sig.parameters) == 1:
        func(ModuleInfo.from_module(module))
    else:
        raise ValueError(f'Invalid callback function: {func.__name__}')


class Registry:
    """ A registry to store the hooks. """

    def __init__(self):
        # A dictionary of which the keys are **the exact module names**.
        self._case_sensitive_registry = defaultdict(
            list
        )  # type: typing.Dict[str, typing.List[HOOK_CALLBACK_FUNC]]

        # A dictionary of which the keys are **the lowercased module names**.
        self._case_insensitive_registry = defaultdict(
            list
        )  # type: typing.Dict[str, typing.List[HOOK_CALLBACK_FUNC]]

    def call_hooks(self, module: types.ModuleType):
        """ Call the hooks for the given module. """
        module_name = _get_module_name(module)
        # First, call the hooks by the exact module name.
        for func in self._case_sensitive_registry[module_name]:
            _call_helper(func, module)

        # Second, call the hooks which are registered with the case-insensitive module name.
        for func in self._case_insensitive_registry[module_name.lower()]:
            _call_helper(func, module)

    def register(self, module_name: str, func: HOOK_CALLBACK_FUNC, *, case_sensitive: bool = True):
        if not callable(func):
            raise TypeError('The parameter `func` must be a callable')

        if case_sensitive:
            self._case_sensitive_registry[module_name].append(func)

            # Call the hook if the module is already imported.
            if module_name in sys.modules:
                _call_helper(func, sys.modules[module_name])
        else:
            # For case-insensitive hooks, we use the lowercased module name as the key.
            lower_module_name = module_name.lower()
            self._case_insensitive_registry[lower_module_name].append(func)

            # Call the hook if the module is already imported.
            for module in list(sys.modules.keys()):
                if module.lower() == lower_module_name:
                    _call_helper(func, sys.modules[module])

    def __repr__(self):
        return f'{self.__class__.__name__}()'


_registry = Registry()


def _call_module_hooks(module: types.ModuleType):
    """ Call the hooks stored in registry for the given module. """
    _registry.call_hooks(module)


def HookedLoader(loader):
    """ Patch the loader to call the hooks when the module is executed. """

    # The `exec_module` and `create_module` methods are the recommended methods for loading modules.
    # And just patching `exec_module` is OK,
    # because the `create_module` is used for creating a module object.
    def patch_exec_module(_exec_module):
        @functools.wraps(_exec_module)
        def wrapper(_module, *args, **kwargs):
            """ The patched `exec_module` method """
            _ret = _exec_module(_module, *args, **kwargs)
            _call_module_hooks(_module)
            return _ret

        setattr(wrapper, _HOOKED_MARK, True)
        return wrapper

    # The `load_module` method is the traditional way to load modules.
    # When the `exec_module` is not available, the `load_module` will be used.
    # See: https://docs.python.org/zh-cn/3/library/importlib.html#importlib.abc.Loader.load_module
    def patch_load_module(_load_module):
        @functools.wraps(_load_module)
        def wrapper(_name, *args, **kwargs):
            """ The patched `load_module` method """
            _module = _load_module(_name, *args, **kwargs)
            if _module is None:
                return None
            _call_module_hooks(_module)
            return _module

        setattr(wrapper, _HOOKED_MARK, True)
        return wrapper

    if hasattr(loader, 'exec_module') and not getattr(loader.exec_module, _HOOKED_MARK, False):
        loader.exec_module = patch_exec_module(loader.exec_module)
    if hasattr(loader, 'load_module') and not getattr(loader.load_module, _HOOKED_MARK, False):
        loader.load_module = patch_load_module(loader.load_module)

    return loader


def patch_finder(finder):
    """ Patch the meta finder to patch the loader when the module is imported.
      And the patched loader will call the hooks when the module is executed
    :param finder: The finder to patch.
    :return: the patched finder.
    """
    if getattr(finder, _HOOKED_MARK, False):
        return finder

    # Patch the `find_spec` method,
    # which is the standard way to find the module spec after Python 3.4.
    def wrap_find_spec(find_spec):
        @functools.wraps(find_spec)
        def wrapper(fullname, path, target=None):
            spec = find_spec(fullname, path, target=target)
            # For namespace packages, the spec.loader is None.
            if spec is not None and spec.loader is not None:
                spec.loader = HookedLoader(spec.loader)
            return spec

        return wrapper

    # Patch the `find_module` method, which is deprecated after Python 3.4, and has been removed in Python 3.12.
    # Before Python 3.12, if the `find_spec` is not available, the `find_module` will be used.
    # See: https://docs.python.org/zh-cn/3.11/library/importlib.html#importlib.abc.Finder.find_module
    # (after 3.12, the section is removed)
    # TODO: Need to be tested
    def wrap_find_module(find_module):
        @functools.wraps(find_module)
        def wrapper(fullname, path):
            loader = find_module(fullname, path)
            if loader is None:  # Handle the case when the loader is None (namespace packages).
                return None
            return HookedLoader(loader)

        return wrapper

    if hasattr(finder, 'find_spec'):
        original_find_spec = finder.find_spec
        setattr(finder, 'find_spec', wrap_find_spec(original_find_spec))
        # Now, the `finder.find_spec` is patched with the wrapper function.
        # Save the original fin`d`_spec method.
        setattr(finder.find_spec, '_orig', original_find_spec)

    if hasattr(finder, 'find_module'):
        original_find_module = finder.find_module
        setattr(finder, 'find_module', wrap_find_module(original_find_module))
        # Now, the `finder.find_module` is patched with the wrapper function.
        # Save the original `find_module` method.
        setattr(finder.find_module, '_orig', original_find_module)

    setattr(finder, _HOOKED_MARK, True)
    return finder


def _unpatch_finder(finder):
    if not getattr(finder, _HOOKED_MARK, False):
        # Not patched
        return finder

    if hasattr(finder, 'find_spec') and hasattr(finder.find_spec, '_orig'):
        original_find_spec = getattr(finder.find_spec, '_orig')
        setattr(finder, 'find_spec', original_find_spec)

    if hasattr(finder, 'find_module'):
        original_find_module = getattr(finder.find_module, '_orig')
        setattr(finder, 'find_module', original_find_module)

    setattr(finder, _HOOKED_MARK, False)
    return finder


class HookMetaPaths(list):
    """ A list-like object to patch `sys.meta_path`.

    :note: We don't reuse the `sys.meta_path` directly because it is a built-in list,
      when adding new finders, we don't know what happens, and the finders may not be patched.
    """
    __hooked__ = True  # Hook mark

    def __init__(self, finders):
        super(HookMetaPaths, self).__init__([patch_finder(f) for f in finders])

    def __setitem__(self, key, val):
        """ When setting a new finder, patch it. """
        super(HookMetaPaths, self).__setitem__(key, patch_finder(val))

    def append(self, finder):
        """ When appending a new finder, patch it. """
        super(HookMetaPaths, self).append(patch_finder(finder))

    def extend(self, finders):
        """ When extending new finders, patch them. """
        super(HookMetaPaths, self).extend([patch_finder(f) for f in finders])

    def insert(self, index, finder):
        """ When inserting a new finder, patch it. """
        super(HookMetaPaths, self).insert(index, patch_finder(finder))


# === APIs === #


def patch_meta_path():
    """ Patch the `sys.meta_path` to hook the all meta path finders.

    :note: It is called by default when importing ihook.
    """
    sys.meta_path = HookMetaPaths(sys.meta_path[:])


def unpatch_meta_path():
    if not hasattr(sys.meta_path, _HOOKED_MARK):
        # Not patched
        return
    sys.meta_path = [_unpatch_finder(f) for f in sys.meta_path]


@typing.overload
def on_import(module_name: str) -> typing.Callable[[HOOK_CALLBACK_FUNC], HOOK_CALLBACK_FUNC]:
    """ A decorator to register a hook function for a given module specified by `module_name`. """
    ...


@typing.overload
def on_import(module_name: str, func: HOOK_CALLBACK_FUNC, *, case_sensitive: bool = True) -> None:
    """ Register a hook function for a given module specified by `module_name`. """
    ...


def on_import(
        module_name: str, func: typing.Optional[HOOK_CALLBACK_FUNC] = None,
        *,
        case_sensitive: bool = True,
):
    """
    Register a hook function for a given module.
    :param module_name: The name of the module to hook.
    :param func: The hook function, if it is not provided, this function will return a decorator.
    :param case_sensitive: Whether the module name is case-sensitive.
    :return:
        - If `func` is not provided, this function will return a decorator.
        - If `func` is provided, this function will return None.

    Example:
    ---------
    ```python
    import ihook
    @ihook.on_import('math')
     def on_math_import():
         print('math imported, the function has no parameters')

    import math
    @ihook.on_import('socket')
     def on_socket_import(module_info: ihook.ModuleInfo):
         print(f'socket imported, the function has one parameter named `module_info`')
         print(f'You can access the module object by `module_info.module_object`: {module_info.module_object}')
         print(f'You can access the module name by `module_info.module_name`: {module_info.module_name}')

    @ihook.on_import('SocKet', case_sensitive=False)
     def on_socket_import_case_insensitively():
         print('socket imported, you can pass the module name in any case if `case_sensitive` is False')

    def on_socket_import_without_decorator():
         print('socket imported, you can also register the hook function without using the decorator')

    ihook.on_import('socket', on_socket_import_without_decorator)
    import socket
    ```
    """
    global _registry

    if func is None:
        def decorator(__dec_param_func):
            _registry.register(
                module_name, __dec_param_func,
                case_sensitive=case_sensitive
            )
            return __dec_param_func

        return decorator
    else:
        _registry.register(
            module_name, func,
            case_sensitive=case_sensitive
        )


def clear_hooks():
    """ Clear all the registered hooks.

    :note:
        - This function will not unpatch the `sys.meta_path`
        - It is convenient for testing.
    """
    global _registry
    _registry = Registry()


def current_patch_method() -> PatchMethods:
    """ Get the current patch method.
    """
    return _PATCH_METHOD


patch_meta_path()
