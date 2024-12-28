import unittest
import ihook
from ihook import _get_module_name as get_module_name  # noqa
from ihook import Registry

class TestUtilFuncs(unittest.TestCase):
    def test_get_module_name(self):
        import math
        self.assertEqual(get_module_name(math), 'math')

        # __main__.__module__ is None here!
        # so the `get_module_name` will return __main__.__name__.
        # See https://docs.python.org/zh-cn/3/reference/import.html#main-spec
        import __main__
        self.assertEqual(get_module_name(__main__), '__main__')

    def test_registry_repr(self):
        self.assertEqual(repr(Registry()), 'Registry()')
