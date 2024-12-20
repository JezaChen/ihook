"""
This module contains utility functions for testing.
"""

import sys
import ihook


class ISensitiveConfigMixin:
    """ A mixin class for sensitive configurations """
    case_sensitive = True

    def on_import_helper(self, name):
        if self.case_sensitive:
            return ihook.on_import(name)
        else:
            return ihook.on_import(scramble_case(name), case_sensitive=False)


def unimport(module_name):
    """ Unimport the module and its submodules from sys.modules """
    for key, mod in dict(sys.modules).items():
        if key.startswith(f'{module_name}.'):
            del sys.modules[key]

            mod_name = getattr(mod, '__name__', None)
            if mod_name in sys.modules:
                del sys.modules[mod_name]
    sys.modules.pop(module_name, None)


def scramble_case(name):
    """
    Scramble the case of the characters in the name randomly.
    >>> scramble_case('hello')
    'HeLLo'  # or 'hElLo', or 'HELLO', etc.
    >>> scramble_case('world')
    'wOrLD'  # or 'WorLD', or 'WORLD', etc.
    """
    import random

    return ''.join(c.upper() if random.randint(0, 1) else c.lower() for c in name)
