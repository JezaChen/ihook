import unittest
import ihook
from tests.utils import unimport, ISensitiveConfigMixin


class TestSimpleCases(unittest.TestCase, ISensitiveConfigMixin):
    case_sensitive = True

    def setUp(self):
        unimport('hashlib')
        unimport('os')
        unimport('importlib')
        unimport('does_not_exist')

    def tearDown(self):
        ihook.clear_hooks()

    def test_trigger_on_import(self):
        """ Test that on_import will trigger when the module is imported """
        triggered = False

        def on_hashlib_import():
            nonlocal triggered
            triggered = True
        self.on_import_direct_func_helper('hashlib', on_hashlib_import)

        import hashlib  # noqa
        self.assertTrue(triggered)

    def test_trigger_on_from_import(self):
        """ Test that on_import will trigger when the module is imported using `from ... import ...` """
        triggered = False

        def on_os_import():
            nonlocal triggered
            triggered = True
        self.on_import_direct_func_helper('os', on_os_import)

        from os import path
        self.assertTrue(triggered)

    def test_trigger_once_on_multiple_imports(self):
        """ Test that on_import will only trigger once when the module is imported multiple times """
        triggered = 0

        def on_hashlib_import():
            nonlocal triggered
            triggered += 1
        self.on_import_direct_func_helper('hashlib', on_hashlib_import)

        import hashlib  # noqa
        import hashlib  # noqa
        self.assertEqual(triggered, 1)

    def test_trigger_on_already_imported_module(self):
        """ Test that on_import will trigger when the module is already imported """
        triggered = False

        import hashlib  # noqa

        def on_hashlib_import():
            nonlocal triggered
            triggered = True
        self.on_import_direct_func_helper('hashlib', on_hashlib_import)

        self.assertTrue(triggered)

    def test_no_trigger_on_not_imported_module(self):
        """ Test that on_import will not trigger when the module is not imported """
        triggered = False

        def on_hashlib_import():
            nonlocal triggered
            triggered = True
        self.on_import_direct_func_helper('hashlib', on_hashlib_import)

        self.assertFalse(triggered)

        # Import hashlib to check if the hook is triggered
        import hashlib  # noqa
        self.assertTrue(triggered)

    def test_no_trigger_on_non_existent_module(self):
        """ Test that on_import will not trigger when the module does not exist """
        triggered = False

        def on_does_not_exist_import():
            nonlocal triggered
            triggered = True
        self.on_import_direct_func_helper('does_not_exist', on_does_not_exist_import)

        self.assertFalse(triggered)

    def test_trigger_on_importlib_import_module(self):
        """ Test that on_import will trigger when the module is imported using importlib """
        triggered = False

        def on_importlib_import():
            nonlocal triggered
            triggered = True
        self.on_import_direct_func_helper('importlib', on_importlib_import)

        import importlib
        importlib.import_module('hashlib')
        self.assertTrue(triggered)

    def test_trigger_on_importlib_reload(self):
        """ Test that on_import will trigger when the module is reloaded using importlib """
        triggered_cnt = 0

        def on_hashlib_reload():
            nonlocal triggered_cnt
            triggered_cnt += 1
        self.on_import_direct_func_helper('hashlib', on_hashlib_reload)

        import hashlib
        self.assertEqual(triggered_cnt, 1)

        import importlib
        importlib.reload(hashlib)
        self.assertEqual(triggered_cnt, 2)

    @unittest.skipIf(
        ihook.current_patch_method() == ihook.PatchMethods.PATCH_META_PATH,
        'When the patch method is `PATCH_META_PATH`, the hook function for `os.path` will not be triggered.\n'
        'See: https://jeza-chen.com/2024/09/28/What-Happens-When-Import-os-path/'
    )
    def test_trigger_on_import_os_path(self):
        """ Test that on_import will trigger when the sub-package `os.path` is imported
        @note: `os` is not a package, but a module, but we can still use `import os.path`
        """
        triggered = False

        def on_os_path_import(module):
            nonlocal triggered
            triggered = True
        self.on_import_direct_func_helper('os.path', on_os_path_import)

        import os.path  # noqa
        self.assertTrue(triggered)

        # Now, the `os.path` module is already imported
        # When we add a new hook, it should be triggered immediately
        triggered = False

        def on_os_path_import2(module):
            nonlocal triggered
            triggered = True
        self.on_import_direct_func_helper('os.path', on_os_path_import2)

        self.assertTrue(triggered)

    def test_trigger_on_already_imported_os_path(self):
        """ Test that on_import will trigger **after** the sub-package `os.path` is imported
        @Note: This is not same as `test_trigger_on_import_os_path`, because the `os.path` module is already imported
          Now, the `self.on_import_helper()` decorator could be triggered immediately
        """
        import os.path
        # Now, the `os.path` module is already imported
        # When we add a new hook, it should be triggered immediately
        triggered = False

        def on_os_path_import(module):
            nonlocal triggered
            triggered = True
        self.on_import_direct_func_helper('os.path', on_os_path_import)

        self.assertTrue(triggered)

    def test_trigger_on_import_ctypes_util(self):
        """ Test that on_import will trigger when the sub-package `ctypes.util` is imported
        @note: Unlike `os`, `ctypes` is a package, so the decorator will be triggered when `ctypes.util` is imported
        """
        triggered = False

        def on_ctypes_util_import(module):
            nonlocal triggered
            triggered = True
        self.on_import_direct_func_helper('ctypes.util', on_ctypes_util_import)

        import ctypes.util  # noqa
        self.assertTrue(triggered)

        # Now, the `ctypes.util` module is already imported
        # When we add a new hook, it should be triggered immediately
        triggered = False

        def on_ctypes_util_import2(module):
            nonlocal triggered
            triggered = True
        self.on_import_direct_func_helper('ctypes.util', on_ctypes_util_import2)

        self.assertTrue(triggered)

    def test_trigger_with_hook_func_params(self):
        """ Test that on_import will trigger with the info of imported module as a parameter """
        # simple case
        triggered_str = ''

        def on_hashlib_import(module):
            nonlocal triggered_str
            triggered_str = module.module_name
        self.on_import_direct_func_helper('hashlib', on_hashlib_import)

        import hashlib  # noqa
        self.assertEqual(triggered_str, 'hashlib')

        # hook imported module
        triggered_str = ''

        def on_hashlib_import2(module):
            nonlocal triggered_str
            triggered_str = module.module_name
        self.on_import_direct_func_helper('hashlib', on_hashlib_import2)

        self.assertEqual(triggered_str, 'hashlib')

    def test_multiple_register(self):
        """ Test that multiple on_import hooks can be registered """
        triggered_cnt = 0

        def on_hashlib_import():
            nonlocal triggered_cnt
            triggered_cnt += 1
        self.on_import_direct_func_helper('hashlib', on_hashlib_import)
        self.on_import_direct_func_helper('os', on_hashlib_import)

        import hashlib  # noqa
        self.assertEqual(triggered_cnt, 1)

        import os  # noqa
        self.assertEqual(triggered_cnt, 2)

    def test_multiple_register2(self):
        triggered_set = []

        def on_hashlib_import(module):
            nonlocal triggered_set
            triggered_set.append(module.module_name)
        self.on_import_direct_func_helper('hashlib', on_hashlib_import)
        self.on_import_direct_func_helper('os', on_hashlib_import)

        import hashlib  # noqa
        self.assertEqual(sorted(triggered_set), ['hashlib'])

        import os  # noqa
        self.assertEqual(sorted(triggered_set), ['hashlib', 'os'])

    def test_multiple_register3(self):
        """ Test that multiple on_import hooks can be registered
        @note: The same hook function can be registered multiple
        """
        triggered_set = []

        def on_import(module):
            nonlocal triggered_set
            triggered_set.append(module.module_name)
        self.on_import_direct_func_helper('hashlib', on_import)
        self.on_import_direct_func_helper('hashlib', on_import)
        self.on_import_direct_func_helper('os', on_import)
        self.on_import_direct_func_helper('os', on_import)
        self.on_import_direct_func_helper('os', on_import)

        import hashlib  # noqa
        self.assertEqual(sorted(triggered_set), ['hashlib', 'hashlib'])

        import os  # noqa
        self.assertEqual(sorted(triggered_set), ['hashlib', 'hashlib', 'os', 'os', 'os'])

    def test_exceptions_handling(self):
        """ Test that exceptions are raised when invalid parameters are passed """
        # pass a not-callable object
        with self.assertRaisesRegex(TypeError, 'The parameter `func` must be a callable'):
            self.on_import_direct_func_helper('test', 'not callable')  # noqa

        # the hook function has more than 1 parameter
        with self.assertRaises(ValueError, msg='Invalid callback function: on_hashlib_import'):
            def on_hashlib_import(module, extra_param):
                pass
            self.on_import_direct_func_helper('hashlib', on_hashlib_import)

            import hashlib  # noqa

    def test_wrong_case_module_name(self):
        """ Test that the hook will not trigger when the module name is in the wrong case """

        triggered = False

        # use the original `on_import`
        def on_hashlib_import():
            nonlocal triggered
            triggered = True
        ihook.on_import('Hashlib', on_hashlib_import)

        import hashlib  # noqa
        self.assertFalse(triggered)

    def test_main_module(self):
        """ Test the behaviour if importing __main__ """
        triggered = False

        def on_main_import():
            nonlocal triggered
            triggered = True
        ihook.on_import('__main__', on_main_import)


        import __main__  # noqa
        self.assertTrue(triggered)

    def test_module_info_param_in_hook_func(self):
        """ Test the module info parameter in the hook function """
        # Place the import statement before the registration
        # Otherwise, the hook function execution will precede the import statement (the import process is not finished)
        # causing `hashlib` to be a free variable
        # (like this error 'cannot access free variable 'hashlib' where it is not associated with a value in enclosing scope')

        import hashlib

        def on_hashlib_import(module):
            # test iter
            nonlocal hashlib
            print(module)
            module_obj, module_name = module
            self.assertEqual(module_name, 'hashlib')
            self.assertEqual(module_obj, hashlib)
        self.on_import_direct_func_helper('hashlib', on_hashlib_import)


class TestCaseInsensitiveParams(TestSimpleCases):
    case_sensitive = False
