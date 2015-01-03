# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Resource hook system interfaces."""

from functools import wraps

from .http import GET


BEFORE_HOOK = 'before'

AFTER_HOOK = 'after'


class request_hook(object):
    """Base class defining the decorator interface from which all other hooks
    inherit.

    The Flask-Arrested hook system allows users to decorate
    :class:`.ApiResource` methods specifying at which points
    during the request/response flow to be called and which, HTTP method
    they apply to.

    Each hook is registerd with an optional name, if no name is provided
    a name will be generated, a hook type and a HTTP method that the hook
    is applicable too.

    Example::

        import arrested

        class MyUserResource(arrested.ApiResource):

            @arrested.request_hook('track_user_foo',
                                   hook=arrested.BEFORE_HOOK,
                                   method=arrested.http.GET)
            def track_user_foo(self):
                do_stuff()

            def get(self, user_id):
                return super(MyUserResource, self).get(user_id)

    In the example above we have registered a hook that will be called before
    all GET requests are dispatched to this ApiResouce.

    .. seealso::

        :class:`.ApiResource`
        :class:`.ApiResourceMetaClass`

    """

    def __init__(self, name=None, hook=None, method=GET, *args, **kwargs):

        try:
            assert hook is not None
        except AssertionError:
            raise NotImplementedError('request_hook must define a valid hook')

        self.name = name
        self.hook = hook
        self.method = method
        self._args = args
        self._kwargs = kwargs

    def __call__(self, f, *args, **kwargs):

        name = self.name or '%s_%s_%s' (f, self.hook, self.method)
        f._register = (name, self.type_, self.method)

        @wraps(f)
        def wrapped(self, *f_args, **f_kwargs):
            return f(self, *f_args, **f_kwargs)
        return wrapped
