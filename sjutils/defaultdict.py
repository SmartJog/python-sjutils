# -*- coding: utf-8 -*-


class DefaultDict(dict):
    """Trivial DefaultDict implementation. Basically returns the
    default value for missing keys.

    TODO: Python2.5 has __missing__ for dict subclasses, we should use
    this (or collections.defaultdict) instead when switching to 2.5"""

    def __init__(self, default=None, *args, **kw):
        dict.__init__(self, *args, **kw)
        self.default = default

    def __getitem__(self, key):
        return self.get(key, self.default)
