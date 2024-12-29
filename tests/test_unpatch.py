import importlib
import unittest
import ihook
from tests.utils import unimport, ISensitiveConfigMixin


class TestClearHooks(unittest.TestCase, ISensitiveConfigMixin):
    case_sensitive = True

    def setUp(self):
        unimport('json')
        unimport('pickle')
        ihook.patch_meta_path()

    def tearDown(self):
        ihook.clear_hooks()
        ihook.unpatch_meta_path()

    def test_clear_hooks(self):
        triggered_cnt = 0

        @self.on_import_decorator_helper('json')
        def on_import_json():
            nonlocal triggered_cnt
            triggered_cnt += 1

        self.assertEqual(triggered_cnt, 0)
        import json  # noqa
        self.assertEqual(triggered_cnt, 1)
        json = importlib.reload(json)
        self.assertEqual(triggered_cnt, 2)

        ihook.clear_hooks()

        json = importlib.reload(json)
        # The hook is cleared, so the counter should not be increased.
        self.assertEqual(triggered_cnt, 2)

        self.on_import_direct_func_helper('json', on_import_json)  # Restore the hook.
        # Remember that the `json` module is already imported, so the hook is triggered immediately.
        self.assertEqual(triggered_cnt, 3)

        json = importlib.reload(json)
        self.assertEqual(triggered_cnt, 4)

    def test_clear_hooks2(self):
        triggered_cnt = 0

        @self.on_import_decorator_helper('json')
        def on_import_json():
            nonlocal triggered_cnt
            triggered_cnt += 1

        self.assertEqual(triggered_cnt, 0)
        ihook.clear_hooks()
        import json  # noqa
        # not triggered
        self.assertEqual(triggered_cnt, 0)
        json = importlib.reload(json)
        # not triggered
        self.assertEqual(triggered_cnt, 0)
        unimport('json')

        # register again
        @self.on_import_decorator_helper('json')
        def on_import_json():
            nonlocal triggered_cnt
            triggered_cnt += 1

        self.assertEqual(triggered_cnt, 0)
        import json
        # triggered
        self.assertEqual(triggered_cnt, 1)
        json = importlib.reload(json)
        # triggered
        self.assertEqual(triggered_cnt, 2)

    def test_clear_hooks3(self):
        triggered_cnt = 0

        @self.on_import_decorator_helper('json')
        def on_import_json():
            nonlocal triggered_cnt
            triggered_cnt += 1

        @self.on_import_decorator_helper('json')
        def on_import_json2():
            nonlocal triggered_cnt
            triggered_cnt += 1

        self.assertEqual(triggered_cnt, 0)
        import json
        self.assertEqual(triggered_cnt, 2)
        json = importlib.reload(json)
        self.assertEqual(triggered_cnt, 4)

        # clear...
        ihook.clear_hooks()
        json = importlib.reload(json)
        self.assertEqual(triggered_cnt, 4)

    def test_clear_hooks4(self):
        triggered_cnt = 0

        @self.on_import_decorator_helper('json')
        def on_import_json():
            nonlocal triggered_cnt
            triggered_cnt += 1

        @self.on_import_decorator_helper('pickle')
        def on_import_pickle():
            nonlocal triggered_cnt
            triggered_cnt += 1

        self.assertEqual(triggered_cnt, 0)
        ihook.clear_hooks()
        import json  # noqa
        import pickle  # noqa
        # not triggered
        self.assertEqual(triggered_cnt, 0)
        json = importlib.reload(json)
        pickle = importlib.reload(pickle)
        # not triggered
        self.assertEqual(triggered_cnt, 0)
        unimport('json')
        unimport('pickle')

        # register again
        @self.on_import_decorator_helper('json')
        def on_import_json():
            nonlocal triggered_cnt
            triggered_cnt += 1

        @self.on_import_decorator_helper('pickle')
        def on_import_pickle():
            nonlocal triggered_cnt
            triggered_cnt += 1

        self.assertEqual(triggered_cnt, 0)
        import json
        # triggered
        self.assertEqual(triggered_cnt, 1)
        json = importlib.reload(json)
        # triggered
        self.assertEqual(triggered_cnt, 2)

        import pickle
        # triggered
        self.assertEqual(triggered_cnt, 3)
        pickle = importlib.reload(pickle)
        # triggered
        self.assertEqual(triggered_cnt, 4)


class TestClearHooksCaseInsensitive(TestClearHooks):
    case_sensitive = False


class TestUnpatchMetaPath(unittest.TestCase, ISensitiveConfigMixin):
    case_sensitive = True

    def setUp(self):
        unimport('json')
        unimport('pickle')
        ihook.patch_meta_path()

    def tearDown(self):
        ihook.clear_hooks()
        ihook.unpatch_meta_path()

    def test_unpatch_meta_path(self):
        triggered_cnt = 0

        @self.on_import_decorator_helper('json')
        def on_import_json():
            nonlocal triggered_cnt
            triggered_cnt += 1

        self.assertEqual(triggered_cnt, 0)
        import json  # noqa
        self.assertEqual(triggered_cnt, 1)
        json = importlib.reload(json)
        self.assertEqual(triggered_cnt, 2)

        ihook.unpatch_meta_path()

        @self.on_import_decorator_helper('pickle')
        def on_import_pickle():
            nonlocal triggered_cnt
            triggered_cnt += 1

        import pickle # noqa

        # because the meta path is unpatched, the hook is not triggered
        self.assertEqual(triggered_cnt, 2)

        pickle = importlib.reload(pickle)
        # The hook is still not triggered.
        self.assertEqual(triggered_cnt, 2)

        json = importlib.reload(json)
        # The hook of json is still not triggered.
        self.assertEqual(triggered_cnt, 2)

    def test_unpatch_meta_path2(self):
        ihook.unpatch_meta_path()
        self.assertFalse(ihook.is_patched())

        triggered_cnt = 0

        @self.on_import_decorator_helper('json')
        def on_import_json():
            nonlocal triggered_cnt
            triggered_cnt += 1

        self.assertEqual(triggered_cnt, 0)
        import json  # noqa
        self.assertEqual(triggered_cnt, 0)
        json = importlib.reload(json)
        self.assertEqual(triggered_cnt, 0)

        # patch again
        ihook.patch_meta_path()
        self.assertTrue(ihook.is_patched())

        @self.on_import_decorator_helper('pickle')
        def on_import_pickle():
            nonlocal triggered_cnt
            triggered_cnt += 1

        import pickle # noqa

        # now the hook is triggered
        self.assertEqual(triggered_cnt, 1)

        pickle = importlib.reload(pickle)
        # The hook is still triggered.
        self.assertEqual(triggered_cnt, 2)

        json = importlib.reload(json)
        # The hook of json can be still triggered.
        self.assertEqual(triggered_cnt, 3)


class TestUnpatchMetaPathCaseInsensitive(TestUnpatchMetaPath):
    case_sensitive = False
