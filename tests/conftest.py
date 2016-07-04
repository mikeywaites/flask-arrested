# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import pytest

from flask import Flask

from arrested import Arrested
from .api import db, TestUsersIndex, TestUserObjectApi


@pytest.yield_fixture(scope='function')
def flask_app(request):

    _app = Flask('arrested_test_app')
    _app.config['TESTING'] = True
    _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    _app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with _app.test_request_context():
        db.init_app(_app)
        yield _app


@pytest.yield_fixture(scope='function')
def client(request, flask_app):

    client = flask_app.test_client()

    yield client


@pytest.yield_fixture(scope='function')
def api(request, flask_app):

    api = Arrested(flask_app)
    api.register(TestUsersIndex)
    api.register(TestUserObjectApi)

    yield api


@pytest.yield_fixture(scope='function')
def db_session():
    db.create_all()
    yield db.session
    db.drop_all()
