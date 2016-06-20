import json
import pytest

try:
    from unittest import mock
except ImportError:
    import mock

from flask import url_for
from arrested.api import hook


from .fixtures import TestResource, TestIndexApi


def test_before_request_hook_registered(flask_app, api, client):

    hook_mock = mock.MagicMock()
    hook_mock.return_value = 0

    class MyTestResource(TestResource):

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

    class MyTestResource(TestResource):

        @hook(methods=['GET', 'POST'], type_='before_request')
        def log(self, *args, **kwargs):

            hook_mock()
            hook_mock.return_value = hook_mock.return_value + 1

        def get(self, *args, **kwargs):
            hook_mock.return_value = hook_mock.return_value - 1

            return '{"test": true}'

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

    class MyTestResource(TestResource):

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

    class MyTestResource(TestResource):

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


def test_index_api_get_objects_not_set(flask_app, api, client):

    api.register(TestIndexApi)

    with pytest.raises(NotImplementedError):
        TestIndexApi().get()


def test_index_api_get_data_not_set(flask_app, api, client):

    api.register(TestIndexApi)

    with pytest.raises(NotImplementedError):
        TestIndexApi().post()


def test_get_index_api(flask_app, api, client):

    class MyIndex(TestIndexApi):

        def get_objects(self):

            return [{'foo': 'bar'}, {'foo': 'baz'}]

    api.register(MyIndex)
    resp = client.get(url_for('api.tests.index'))

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == [{'foo': 'bar'}, {'foo': 'baz'}]


def test_post_index_api(flask_app, api, client):

    class MyIndex(TestIndexApi):

        methods = ['GET', 'POST']

        def get_data(self):

            return [{'foo': 'bar'}, {'foo': 'baz'}]

    api.register(MyIndex)
    resp = client.post(url_for('api.tests.index'))

    assert resp.status_code == 201
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == [{'foo': 'bar'}, {'foo': 'baz'}]
