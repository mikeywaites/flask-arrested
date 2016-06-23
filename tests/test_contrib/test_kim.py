import pytest
import json

from flask import url_for, request

from kim import Mapper, field

from arrested import Api
from arrested.contrib.kim import (
    KimRequestHandler, KimResponseHandler, ListableResource, CreateableResource)

from ..fixtures import MockUser


class UserMapper(Mapper):

    __type__ = MockUser

    id = field.Integer(read_only=True)
    username = field.String()
    email = field.String()
    is_admin = field.Boolean(default=False, required=False)

    __roles__ = {
        'public': ['username']
    }


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
        MockUser(id='1', username='mike',
                 email='mike@mike.com', is_admin=True),
        MockUser(id='2', username='jack',
                 email='jack@jack.com', is_admin=False)
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


def test_kim_listable_resource(api, client):

    class MyTestResource(Api, ListableResource):

        mapper_class = UserMapper
        endpoint_name = 'test_resource'
        url = '/tests'

        def get_objects(self, *args, **kwargs):

            users = [
                MockUser(id='1', username='mike', email='mike@mike.com'),
                MockUser(id='2', username='jack', email='jack@jack.com')]

            return users

    api.register(MyTestResource)

    resp = client.get(url_for('api.test_resource'))
    assert resp.status_code == 200

    data = json.loads(resp.data.decode('utf-8'))

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0] == {
        'username': 'mike', 'email': 'mike@mike.com',
        'id': '1',
        'is_admin': False}
    assert data[1] == {
        'username': 'jack', 'email': 'jack@jack.com',
        'id': '2',
        'is_admin': False}


def test_kim_listable_resource_with_role(api, client):

    class MyTestResource(Api, ListableResource):

        mapper_class = UserMapper
        endpoint_name = 'test_resource'
        url = '/tests'
        serialize_role = 'public'

        def get_objects(self, *args, **kwargs):

            users = [
                MockUser(id='1', username='mike', email='mike@mike.com'),
                MockUser(id='2', username='jack', email='jack@jack.com')]

            return users

    api.register(MyTestResource)

    resp = client.get(url_for('api.test_resource'))
    assert resp.status_code == 200

    data = json.loads(resp.data.decode('utf-8'))

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0] == {'username': 'mike'}
    assert data[1] == {'username': 'jack'}


def test_kim_createable_resource(api, client):

    class MyTestResource(Api, CreateableResource):

        mapper_class = UserMapper
        endpoint_name = 'test_resource'
        url = '/tests'
        methods = ['GET', 'POST']

        def get_data(self):

            data = request.json
            return data

    api.register(MyTestResource)

    data = {'username': 'mike', 'email': 'mike@mike.com'}

    resp = client.post(url_for('api.test_resource'),
                       data=json.dumps(data),
                       content_type='application/json')

    assert resp.status_code == 201

    data = json.loads(resp.data.decode('utf-8'))

    assert data == {
        'username': 'mike', 'email': 'mike@mike.com',
        'id': '1',
        'is_admin': False}
