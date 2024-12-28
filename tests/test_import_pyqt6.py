import unittest
import ihook
from tests.utils import unimport, ISensitiveConfigMixin


class TestImportPyQt6(unittest.TestCase, ISensitiveConfigMixin):
    """ Test cases for third-party module PyQt6 """
    case_sensitive = True

    def setUp(self):
        unimport('PyQt6')
        unimport('PyQt6.QtCore')
        unimport('PyQt6.QtWidgets')
        unimport('PyQt6.QtGui')

    def tearDown(self):
        ihook.clear_hooks()

    def test_trigger_on_import_PyQt6(self):
        """ Test that on_import will trigger when the module is imported """
        triggered = False

        @self.on_import_decorator_helper('PyQt6')
        def on_import_PyQt6():
            nonlocal triggered
            triggered = True

        import PyQt6  # noqa
        self.assertTrue(triggered)

    def test_trigger_on_import_PyQt6_sub_package(self):
        """ Test that on_import will trigger when the sub-package is imported """
        triggered = False

        @self.on_import_decorator_helper('PyQt6.QtCore')
        def on_import_PyQt6_QtCore():
            nonlocal triggered
            triggered = True

        import PyQt6.QtCore  # noqa
        self.assertTrue(triggered)

    def test_trigger_on_import_PyQt6_multiple_hooks(self):
        """ Test that on_import will trigger when the module is imported """
        triggered = 0

        @self.on_import_decorator_helper('PyQt6')
        def on_import_PyQt6():
            nonlocal triggered
            triggered += 1

        @self.on_import_decorator_helper('PyQt6')
        def on_import_PyQt6_2():
            nonlocal triggered
            triggered += 1

        import PyQt6  # noqa
        self.assertEqual(triggered, 2)

        @self.on_import_decorator_helper('PyQt6')
        def on_import_PyQt6_3():
            nonlocal triggered
            triggered += 1

        self.assertEqual(triggered, 3)

    def test_trigger_on_import_PyQt6_sub_package_multiple_hooks(self):
        """ Test that on_import will trigger when the sub-package is imported """
        triggered = 0

        @self.on_import_decorator_helper('PyQt6.QtCore')
        def on_import_PyQt6_QtCore():
            nonlocal triggered
            triggered += 1

        @self.on_import_decorator_helper('PyQt6.QtCore')
        def on_import_PyQt6_QtCore_2():
            nonlocal triggered
            triggered += 1

        import PyQt6.QtCore  # noqa
        self.assertEqual(triggered, 2)

        @self.on_import_decorator_helper('PyQt6.QtCore')
        def on_import_PyQt6_QtCore_3():
            nonlocal triggered
            triggered += 1

        self.assertEqual(triggered, 3)


class TestImportPyQt6CaseInsensitive(TestImportPyQt6):
    """ Test cases for third-party module PyQt6 for case-insensitive cases """
    case_sensitive = False
