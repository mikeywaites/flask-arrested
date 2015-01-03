# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


from flask.views import MethodView


class ApiResourceMetaclass(type):

    def __new__(mcs, name, bases, attrs):

        attrs['_hooks'] = {
            'GET': {},
            'POST': {},
            'PUT': {},
            'DELETE': {}
        }
        for key, val in attrs.iteritems():
            if getattr(val, '_register', None):
                mcs.register_hook(attrs['_hooks'], val)

        new_class = (super(ApiResourceMetaclass, mcs)
                     .__new__(mcs, name, bases, attrs))

        return new_class

    def register_hook(self, hook_data, hook):
        name, type_, method = hook._register
        hook_data[method].setdefault(type_, {})
        hook_data[method][type_][name] = hook

        return hook_data


class ApiResourceOpts(object):

    def __init__(self, meta):

        self.roles = getattr(meta, 'roles', {})


class ApiResource(object):

    __metaclass__ = ApiResourceMetaclass

    class Meta:
        pass

    def __init__(self, data=None, input=None):
        self.opts = ApiResourceOpts(self.Meta)
