
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

import pytest
from kim import Mapper, field

from arrested.handlers import Handler, KimRequestHandler, KimResponseHandler


class MockUser(object):

    def __init__(self, id=None, username=None, email=None, is_admin=None):

        self.id = id
        self.username = username
        self.email = email
        self.is_admin = is_admin


class UserMapper(Mapper):

    __type__ = MockUser

    id = field.Integer(read_only=True)
    username = field.String()
    email = field.String()
    is_admin = field.Boolean(default=False, required=False)


def test_handler_sets_params():

    handler = Handler(one=1, two=2)
    assert handler.params == {'one': 1, 'two': 2}


def test_handler_to_json():

    handler = Handler()
    handler.data = {'one': 1}
    assert handler.to_json() == '{"one": 1}'


def test_handler_from_json():

    handler = Handler()
    handler.data = '{"one": 1}'
    assert handler.from_json() == {"one": 1}


def test_handler_must_implement_handle_method():

    handler = Handler()
    with pytest.raises(NotImplementedError):
        handler.process({'one': 1})


def test_kim_handler_requires_mapper():

    handler = KimRequestHandler()
    with pytest.raises(Exception):
        handler.process({'one': 1})


def test_kim_request_handler():

    data = {'username': 'mike', 'email': 'mike@mike.com'}
    request = KimRequestHandler(mapper_class=UserMapper)
    request.process(data)

    assert isinstance(request.data, MockUser)
    assert request.data.username == 'mike'
    assert request.data.email == 'mike@mike.com'
    assert request.data.is_admin is False


def test_kim_request_handler_many():

    data = [
        {'username': 'mike', 'email': 'mike@mike.com'},
        {'username': 'jack', 'email': 'jack@jack.com'}
    ]
    request = KimRequestHandler(mapper_class=UserMapper, many=True)
    request.process(data)

    assert isinstance(request.data[0], MockUser)
    assert request.data[0].username == 'mike'
    assert request.data[0].email == 'mike@mike.com'
    assert request.data[0].is_admin is False

    assert isinstance(request.data[1], MockUser)
    assert request.data[1].username == 'jack'
    assert request.data[1].email == 'jack@jack.com'
    assert request.data[1].is_admin is False


def test_kim_request_handler_invalid():

    data = {'email': 'mike@mike.com'}
    request = KimRequestHandler(mapper_class=UserMapper)
    request.process(data)

    assert request.errors is not None
    assert request.errors == {'username': 'This is a required field'}


def test_kim_response_handler():

    user = MockUser(username='mike', email='mike@mike.com', is_admin=True)

    request = KimResponseHandler(mapper_class=UserMapper)
    request.process(user)

    assert isinstance(request.data, dict)
    assert request.data['username'] == 'mike'
    assert request.data['email'] == 'mike@mike.com'
    assert request.data['is_admin'] is True


def test_kim_response_handler_many():

    users = [
        MockUser(id='1', username='mike', email='mike@mike.com', is_admin=True),
        MockUser(id='2', username='jack', email='jack@jack.com', is_admin=False)
    ]

    request = KimResponseHandler(mapper_class=UserMapper, many=True)
    request.process(users)

    assert isinstance(request.data, list)
    assert request.data[0] == {
        'username': 'mike', 'email': 'mike@mike.com',
        'id': '1',
        'is_admin': True}
    assert request.data[1] == {
        'username': 'jack', 'email': 'jack@jack.com',
        'id': '2',
        'is_admin': False}
