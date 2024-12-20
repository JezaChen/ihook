import unittest
import ihook
from tests.utils import unimport, ISensitiveConfigMixin

import sys
import pathlib

file_path = pathlib.Path(__file__).resolve()
tests_dir_path = file_path.parent
custom_package_sample_dir_name = 'custom_package_sample'

# Add the custom_package_sample directory to the path
sys.path.append(str(tests_dir_path / custom_package_sample_dir_name))


# When importing `pkg_a`, it will import `mod_b` and `pkg_d` as well.
# When importing `pkg_a.pkg_d`, it will import `pkg_a.pkg_d.mod_e` as well.
# When importing `pkg_a.pkg_g`, it will import `pkg_a.pkg_g.mod_h` as well.
# When each module is imported, a message will be printed to the console.


class TestCustomPackageImport(unittest.TestCase, ISensitiveConfigMixin):
    case_sensitive = True

    def setUp(self):
        unimport('pkg_a')

    def tearDown(self):
        ihook.clear_hooks()

    def _init_triggered_info(self) -> dict:
        triggered = {
            'pkg_a': False,
            'pkg_a.mod_b': False,
            'pkg_a.mod_c': False,
            'pkg_a.pkg_d': False,
            'pkg_a.pkg_g': False,
            'pkg_a.pkg_d.mod_e': False,
            'pkg_a.pkg_d.mod_f': False,
            'pkg_a.pkg_g.mod_h': False,
            'pkg_a.pkg_g.mod_i': False,
        }

        @ihook.on_import('pkg_a')
        def on_pkg_a_import():
            triggered['pkg_a'] = True

        @ihook.on_import('pkg_a.mod_b')
        def on_pkg_a_mod_b_import():
            triggered['pkg_a.mod_b'] = True

        @ihook.on_import('pkg_a.mod_c')
        def on_pkg_a_mod_c_import():
            triggered['pkg_a.mod_c'] = True

        @ihook.on_import('pkg_a.pkg_d')
        def on_pkg_a_pkg_d_import():
            triggered['pkg_a.pkg_d'] = True

        @ihook.on_import('pkg_a.pkg_g')
        def on_pkg_a_pkg_g_import():
            triggered['pkg_a.pkg_g'] = True

        @ihook.on_import('pkg_a.pkg_d.mod_e')
        def on_pkg_a_pkg_d_mod_e_import():
            triggered['pkg_a.pkg_d.mod_e'] = True

        @ihook.on_import('pkg_a.pkg_d.mod_f')
        def on_pkg_a_pkg_d_mod_f_import():
            triggered['pkg_a.pkg_d.mod_f'] = True

        @ihook.on_import('pkg_a.pkg_g.mod_h')
        def on_pkg_a_pkg_g_mod_h_import():
            triggered['pkg_a.pkg_g.mod_h'] = True

        @ihook.on_import('pkg_a.pkg_g.mod_i')
        def on_pkg_a_pkg_g_mod_i_import():
            triggered['pkg_a.pkg_g.mod_i'] = True

        return triggered

    def _assert_triggered_info(self, triggered: dict, *expected_triggered: str):
        for key, value in triggered.items():
            if key in expected_triggered:
                self.assertTrue(value, f'{key} was not triggered')
            else:
                self.assertFalse(value, f'{key} was triggered')

    def test_trigger_on_import_pkg_a(self):
        """ Test that on_import will trigger when importing `pkg_a` """
        triggered = self._init_triggered_info()

        # If we import pkg_a, it will import mod_b and pkg_d as well.
        import pkg_a  # noqa

        self._assert_triggered_info(
            triggered,
            'pkg_a',
            'pkg_a.mod_b', 'pkg_a.pkg_d',
            'pkg_a.pkg_d.mod_e',
        )

    def test_trigger_on_import_pkg_a_pkg_g(self):
        """ Test that on_import will trigger when importing `pkg_a.pkg_g` """
        triggered = self._init_triggered_info()

        # If we import pkg_a, it will import mod_b and pkg_d as well.
        import pkg_a.pkg_g  # noqa

        # === Python Documentation ===
        # This name will be used in various phases of the import search,
        # and it may be the dotted path to a submodule,
        # e.g. foo.bar.baz. In this case, Python first tries to import foo, then foo.bar, and finally foo.bar.baz.
        # If any of the intermediate imports fail, a ModuleNotFoundError is raised.
        # === End ===

        self._assert_triggered_info(
            triggered,
            'pkg_a.pkg_g',
            'pkg_a.pkg_g.mod_h',  # when importing pkg_a.pkg_g, it will import pkg_a.pkg_g.mod_h as well
            # import `pkg_a` automatically before `pkg_a.pkg_g`
            'pkg_a',
            'pkg_a.mod_b', 'pkg_a.pkg_d',
            'pkg_a.pkg_d.mod_e',
        )

    def test_trigger_on_import_pkg_a_pkg_g_mod_i(self):
        """ Test that on_import will trigger when importing `pkg_a.pkg_g.mod_i` """
        triggered = self._init_triggered_info()

        # If we import pkg_a, it will import mod_b and pkg_d as well.
        import pkg_a.pkg_g.mod_i  # noqa

        self._assert_triggered_info(
            triggered,
            'pkg_a.pkg_g.mod_i',
            # import `pkg_a` automatically before `pkg_a.pkg_g`
            'pkg_a',
            'pkg_a.mod_b', 'pkg_a.pkg_d',
            'pkg_a.pkg_d.mod_e',
            # import `pkg_a.pkg_g` automatically before `pkg_a.pkg_g.mod_i`
            'pkg_a.pkg_g', 'pkg_a.pkg_g.mod_h',
        )

    def test_trigger_on_importlib_import_module_pkg_a(self):
        """ Test that on_import will trigger when importing `pkg_a` via importlib.import_module """
        triggered = self._init_triggered_info()

        # If we import pkg_a, it will import mod_b and pkg_d as well.
        import importlib
        importlib.import_module('pkg_a')

        self._assert_triggered_info(
            triggered,
            'pkg_a',
            'pkg_a.mod_b', 'pkg_a.pkg_d',
            'pkg_a.pkg_d.mod_e',
        )

    def test_trigger_on_importlib_import_module_pkg_a_pkg_g(self):
        """ Test that on_import will trigger when importing `pkg_a.pkg_g` via importlib.import_module """
        triggered = self._init_triggered_info()

        # If we import pkg_a, it will import mod_b and pkg_d as well.
        import importlib
        importlib.import_module('pkg_a.pkg_g')

        self._assert_triggered_info(
            triggered,
            'pkg_a.pkg_g',
            'pkg_a.pkg_g.mod_h',  # when importing pkg_a.pkg_g, it will import pkg_a.pkg_g.mod_h as well
            # import `pkg_a` automatically before `pkg_a.pkg_g`
            'pkg_a',
            'pkg_a.mod_b', 'pkg_a.pkg_d',
            'pkg_a.pkg_d.mod_e',
        )


class TestCustomPackageImportCaseInsensitive(TestCustomPackageImport, ISensitiveConfigMixin):
    case_sensitive = False
