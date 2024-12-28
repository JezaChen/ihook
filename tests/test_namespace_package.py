import unittest
import ihook
from tests.utils import unimport, ISensitiveConfigMixin

import sys
import pathlib

file_path = pathlib.Path(__file__).resolve()
tests_dir_path = file_path.parent
namespace_package_sample_dir_name = 'namespace_package_sample'

# Add the `namespace_package_sample/local` and `namespace_package_sample/third_party` directories to the path
sys.path.extend(
    [
        str(tests_dir_path / namespace_package_sample_dir_name / 'local'),
        str(tests_dir_path / namespace_package_sample_dir_name / 'third_party')
    ]
)


class TestNamespacePackageImport(unittest.TestCase, ISensitiveConfigMixin):
    case_sensitive = True

    def setUp(self):
        unimport('package.a')
        unimport('package.b')

    def tearDown(self):
        ihook.clear_hooks()

    def test_trigger_on_import(self):
        """ Test that on_import will trigger when the namespace package is imported """
        triggered_a = triggered_b = False

        @self.on_import_decorator_helper('package.a')
        def on_package_a_import():
            nonlocal triggered_a
            triggered_a = True

        import package.a  # noqa
        self.assertTrue(triggered_a)
        self.assertFalse(triggered_b)

        @self.on_import_decorator_helper('package.b')
        def on_package_b_import():
            nonlocal triggered_b
            triggered_b = True

        import package.b  # noqa
        self.assertTrue(triggered_a)

    def test_trigger_on_importlib_import_module(self):
        """ Test that on_import will trigger when the module is imported via importlib.import_module """
        triggered_a = triggered_b = False

        @self.on_import_decorator_helper('package.a')
        def on_package_a_import():
            nonlocal triggered_a
            triggered_a = True

        import importlib
        _ = importlib.import_module('package.a')
        self.assertTrue(triggered_a)
        self.assertFalse(triggered_b)

        @self.on_import_decorator_helper('package.b')
        def on_package_b_import():
            nonlocal triggered_b
            triggered_b = True

        _ = importlib.import_module('package.b')
        self.assertTrue(triggered_b)

    def test_trigger_on_importlib_reload(self):
        """ Test that on_import will trigger when the module is reloaded via importlib.reload """
        triggered_cnt_a = triggered_cnt_b =  0

        @self.on_import_decorator_helper('package.a')
        def on_package_a_import():
            nonlocal triggered_cnt_a
            triggered_cnt_a += 1

        import importlib
        package_a = importlib.import_module('package.a')
        self.assertEqual(triggered_cnt_a, 1)
        importlib.reload(package_a)
        self.assertEqual(triggered_cnt_a, 2)
        self.assertEqual(triggered_cnt_b, 0)

        @self.on_import_decorator_helper('package.b')
        def on_package_b_import():
            nonlocal triggered_cnt_b
            triggered_cnt_b += 1

        package_b = importlib.import_module('package.b')
        self.assertEqual(triggered_cnt_b, 1)
        importlib.reload(package_b)
        self.assertEqual(triggered_cnt_b, 2)


class TestNamespacePackageImportCaseInsensitive(TestNamespacePackageImport):
    case_sensitive = False
