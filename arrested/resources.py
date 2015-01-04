# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


from flask import request
from flask.views import View
from flask._compat import with_metaclass

from .hooks import BEFORE_HOOK


class ApiResourceMetaType(type):

    def __new__(mcs, name, bases, attrs):

        attrs['_hooks'] = {
            'get': {},
            'post': {},
            'put': {},
            'delete': {}
        }
        for key, val in attrs.iteritems():
            if getattr(val, '_register', None):
                mcs.register_hook(attrs['_hooks'], val)

        new_class = (super(ApiResourceMetaType, mcs)
                     .__new__(mcs, name, bases, attrs))

        return new_class

    @classmethod
    def register_hook(self, hook_data, func):

        name, hook, method = func._register
        hook_data[method.lower()].setdefault(hook, {})
        hook_data[method.lower()][hook][name] = func

        return hook_data


class ApiResourceOpts(object):

    def __init__(self, meta):

        self.roles = getattr(meta, 'roles', {})


class ApiResource(with_metaclass(ApiResourceMetaType, View)):

    __metaclass__ = ApiResourceMetaType

    class Meta:
        pass

    def __init__(self, data=None, input=None):
        self.opts = ApiResourceOpts(self.Meta)

    def get_hooks(self, hook):

        meth_name = self.request.method.lower()
        for _, func in self._hooks[meth_name].get(hook, {}).iteritems():
            yield func

    def dispatch_request(self, *args, **kwargs):

        self.request = request
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        assert meth is not None, 'Unimplemented method %r' % request.method

        for func in self.get_hooks(BEFORE_HOOK):
            func(self, request)

        try:
            return meth(*args, **kwargs)
        except Exception as e:
            for func in self.get_hooks('error'):
                func(self, request)
            raise e
        finally:
            for func in self.get_hooks('after'):
                func(self, request)
