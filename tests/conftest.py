# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import pytest
import arrested

from flask import Flask, abort


class UserApi(arrested.ApiResource):

    @arrested.request_hook(hook=arrested.BEFORE_HOOK, method=arrested.GET)
    def foo(self, request):
        abort(400)

    def get(self):
        return 'foo', 200


@pytest.yield_fixture(scope='session')
def app(request):

    _app = Flask('arrested')
    _app.testing = True
    _app.add_url_rule('/', view_func=UserApi.as_view('user'))
    yield _app
