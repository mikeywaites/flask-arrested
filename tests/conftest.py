# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import pytest

from flask import Flask

from arrested import Arrested


@pytest.yield_fixture(scope='function')
def flask_app(request):

    _app = Flask('arrested_test_app')

    with _app.test_request_context():
        yield _app


@pytest.yield_fixture(scope='function')
def client(request, flask_app):

    client = flask_app.test_client()

    yield client


@pytest.yield_fixture(scope='function')
def api(request, flask_app):

    api = Arrested(flask_app)

    yield api
