import json

try:
    from unittest import mock
except ImportError:
    import mock

from flask import url_for
from arrested import Arrested
from arrested.api import hook, Api, ListableResource, CreateableResource

from .api import User, TestUsersIndex, create_users


def test_before_request_hook_registered(flask_app, client):

    api = Arrested(flask_app)

    hook_mock = mock.MagicMock()
    hook_mock.return_value = 0

    class MyTestResource(Api, ListableResource):

        endpoint_name = 'test_resource'
        url = '/tests'

        @hook(methods=['GET'], type_='before_request')
        def pre_get(self, *args, **kwargs):

            hook_mock()
            hook_mock.return_value = hook_mock.return_value + 1

        def get(self, *args, **kwargs):
            hook_mock.return_value = hook_mock.return_value - 1

            return '{"test": true}'

    api.register(MyTestResource)

    client.get(url_for('api.test_resource'))

    hook_mock.assert_called_once_with()
    assert hook_mock.return_value == 0


def test_before_request_hook_multile_verbs(flask_app, api, client):

    hook_mock = mock.MagicMock()
    hook_mock.return_value = 0

    class MyTestResource(Api, CreateableResource, ListableResource):

        endpoint_name = 'test_resource'
        url = '/tests'

        @hook(methods=['GET', 'POST'], type_='before_request')
        def log(self, *args, **kwargs):

            hook_mock()
            hook_mock.return_value = hook_mock.return_value + 1

        def get(self, *args, **kwargs):
            hook_mock.return_value = hook_mock.return_value - 1

            return '{"test": true}'

        def save_object(self):
            pass

        def post(self, *args, **kwargs):
            hook_mock.return_value = hook_mock.return_value + 2

            return '{"test": true}'

    api.register(MyTestResource)

    client.get(url_for('api.test_resource'))

    assert hook_mock.return_value == 0

    client.post(url_for('api.test_resource'))

    assert hook_mock.return_value == 3


def test_before_request_hook_ignored(flask_app, api, client):

    hook_mock = mock.MagicMock()
    hook_mock.return_value = 0

    class MyTestResource(Api, ListableResource):

        endpoint_name = 'test_resource'
        url = '/tests'

        @hook(methods=['POST'], type_='before_request')
        def pre_post(self, *args, **kwargs):

            hook_mock()
            hook_mock.return_value = hook_mock.return_value + 1

        def get(self, *args, **kwargs):
            hook_mock.return_value = hook_mock.return_value - 1

            return '{"test": true}'

    api.register(MyTestResource)

    client.get(url_for('api.test_resource'))

    assert not hook_mock.called
    assert hook_mock.return_value == -1


def test_after_request_hook_registered(flask_app, api, client):

    hook_mock = mock.MagicMock()
    hook_mock.return_value = 0

    class MyTestResource(Api, ListableResource):

        endpoint_name = 'test_resource'
        url = '/tests'

        @hook(methods=['GET'], type_='after_request')
        def post_get(self, request, *args, **kwargs):

            hook_mock()
            hook_mock.return_value = hook_mock.return_value + 2

            return request

        def get(self, *args, **kwargs):
            hook_mock.return_value = hook_mock.return_value - 1

            return '{"test": true}'

    api.register(MyTestResource)

    client.get(url_for('api.test_resource'))

    hook_mock.assert_called_once_with()
    assert hook_mock.return_value == 1


def test_get_index_api(flask_app, api, client, db_session):

    u1, u2 = create_users(db_session, 2)

    resp = client.get(url_for('api.users.index'))

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'meta': {
            'total_pages': 1,
            'total_objects': 2,
            'per_page': 10,
            'current_page': 1,
            'next_page': None,
            'prev_page': None,
        },
        'payload': [
            {'id': u1.id, 'name': u1.name, 'is_admin': False},
            {'id': u2.id, 'name': u2.name, 'is_admin': False}
        ]
    }


def test_get_index_api_per_page(flask_app, api, client, db_session):

    u1, u2 = create_users(db_session, 2)

    resp = client.get(url_for('api.users.index', per_page=1))

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    exp = {
        'meta': {
            'total_pages': 2,
            'total_objects': 2,
            'per_page': 1,
            'current_page': 1,
            'next_page': 2,
            'prev_page': None,
        },
        'payload': [
            {'id': u1.id, 'name': u1.name, 'is_admin': False},
        ]
    }
    assert data == exp

    # ensure it defaults to the `num_per_page` param when an invalid type
    # is provided.

    resp = client.get(url_for('api.users.index', per_page='notanint'))

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'meta': {
            'total_pages': 1,
            'total_objects': 2,
            'per_page': 10,
            'current_page': 1,
            'next_page': None,
            'prev_page': None,
        },
        'payload': [
            {'id': u1.id, 'name': u1.name, 'is_admin': False},
            {'id': u2.id, 'name': u2.name, 'is_admin': False},
        ]
    }


def test_get_index_api_specify_page(flask_app, api, client, db_session):

    u1, u2 = create_users(db_session, 2)

    resp = client.get(url_for('api.users.index', per_page=1, page=2))

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'meta': {
            'total_pages': 2,
            'total_objects': 2,
            'per_page': 1,
            'current_page': 2,
            'next_page': None,
            'prev_page': 1,
        },
        'payload': [
            {'id': u2.id, 'name': u2.name, 'is_admin': False},
        ]
    }

    # provide a page that doesn't exist
    resp = client.get(url_for('api.users.index', per_page=1, page=3))

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'meta': {
            'total_pages': 2,
            'total_objects': 2,
            'per_page': 1,
            'current_page': 3,
            'next_page': None,
            'prev_page': 2,
        },
        'payload': [
        ]
    }

    # provide a invalid type for page defaults to page 1
    resp = client.get(url_for('api.users.index', per_page=1, page='notanint'))

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'meta': {
            'total_pages': 2,
            'total_objects': 2,
            'per_page': 1,
            'current_page': 1,
            'next_page': 2,
            'prev_page': None,
        },
        'payload': [
            {'id': u1.id, 'name': u1.name, 'is_admin': False},
        ]
    }


def test_get_index_api_no_pagination(flask_app, api, client, db_session):

    u1, u2 = create_users(db_session, 2)

    class MyTestResource(TestUsersIndex):

        url = '/test'
        endpoint_name = 'users.index.2'
        paginate = False

    api.register(MyTestResource)

    resp = client.get(url_for('api.users.index.2', per_page=1, page=2))

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'payload': [
            {'id': u1.id, 'name': u1.name, 'is_admin': False},
            {'id': u2.id, 'name': u2.name, 'is_admin': False},
        ]
    }


def test_post_index_api(flask_app, api, client, db_session):

    data = {
        'name': 'mike',
        'password': '123123'
    }
    resp = client.post(url_for('api.users.index'),
                       data=json.dumps(data),
                       content_type='application/json')

    assert resp.status_code == 201
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'payload': {
            'id': 'mike-id', 'name': 'mike', 'is_admin': False
        }
    }

    user = db_session.query(User).get(data['payload']['id'])

    assert user is not None
    assert user.name == 'mike'
    assert user.password == '123123'
    assert user.is_admin is False


def test_post_index_api_with_errors(flask_app, api, client, db_session):

    data = {}
    resp = client.post(url_for('api.users.index'),
                       data=json.dumps(data),
                       content_type='application/json')

    assert resp.status_code == 400
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'payload': {
            'error': True,
            'errors': {
                'name': 'This is a required field',
                'password': 'This is a required field',
            }
        }
    }


def test_get_object_api(flask_app, api, client, db_session):

    u1, = create_users(db_session, 1)
    resp = client.get(url_for('api.users.object', obj_id=u1.id))

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'payload': {
            'id': u1.id, 'name': u1.name, 'is_admin': False
        }
    }


def test_get_object_does_not_exist(flask_app, api, client, db_session):

    u1, = create_users(db_session, 1)
    resp = client.get(url_for('api.users.object', obj_id='notvalid'))

    assert resp.status_code == 404
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {'payload': {
        'error': True, 'errors': {'not_found': 'Object not found'}}}


def test_put_object_api(flask_app, api, client, db_session):

    u1, = create_users(db_session, 1)
    data = {
        'name': 'New Name'
    }
    resp = client.put(
        url_for('api.users.object', obj_id=u1.id),
        data=json.dumps(data), content_type='application/json')

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'payload': {
            'id': u1.id, 'name': 'New Name', 'is_admin': False
        }
    }

    user = db_session.query(User).get(data['payload']['id'])
    assert user.name == 'New Name'


def test_patch_object_api(flask_app, api, client, db_session):

    u1, = create_users(db_session, 1)
    data = {}
    resp = client.patch(
        url_for('api.users.object', obj_id=u1.id),
        data=json.dumps(data), content_type='application/json')

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'payload': {
            'id': u1.id, 'name': u1.name, 'is_admin': False,
        }
    }

    user = db_session.query(User).get(data['payload']['id'])
    assert user.name == u1.name


def test_delete_object_api(flask_app, api, client, db_session):

    u1, = create_users(db_session, 1)
    resp = client.delete(
        url_for('api.users.object', obj_id=u1.id))

    assert resp.status_code == 204
    assert resp.content_type == 'application/json'

    user = db_session.query(User).get(u1.id)
    assert user is None
