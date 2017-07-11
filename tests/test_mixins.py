import json
import pytest

from werkzeug.exceptions import NotFound
from arrested import (
    Endpoint, GetListMixin, GetObjectMixin,
    ResponseHandler, RequestHandler, ObjectMixin
)
from unittest import mock

from tests.endpoints import CharactersEndpoint, CharacterEndpoint


GET = pytest.mark.GET
POST = pytest.mark.POST
GET_OBJ = pytest.mark.GET_OBJ
PUT = pytest.mark.PUT
DELETE = pytest.mark.DELETE


class GetListEndpoint(CharactersEndpoint):

    pass


def test_get_list_mixin_handle_get_request_no_objects(app):
    """assert the GetListMixin handles null objects correctly in the response payload.
    """

    with mock.patch.object(GetListEndpoint, 'get_objects', return_value=None) as mock_method:
        endpoint = GetListEndpoint()
        resp = endpoint.get()
        assert mock_method.called
        assert resp.data.decode("utf-8") == '{"payload": null}'


def test_get_list_mixin_handle_get_request_get_objects_not_defined(app):
    """assert the GetListMixin interface
    """

    class GetListEndpoint(Endpoint, GetListMixin):
        pass

    with pytest.raises(NotImplementedError):
        endpoint = GetListEndpoint()
        endpoint.get()


def test_get_list_mixin_handle_request_sets_response_attr(app):
    """Ensure that when the handle_get_request method is called the ResponseHandler is
    instantiated and set against the Endpoint.response attribute.
    """

    endpoint = GetListEndpoint()
    endpoint.get()

    assert isinstance(endpoint.response, ResponseHandler)


def test_get_list_mixin_sets_objects(app):
    """Ensure objetcs param is set whenever a get request is handled by the mixin
    """

    endpoint = GetListEndpoint()
    mock_objects = [{'foo': 'bar'}]
    with mock.patch.object(GetListEndpoint, 'get_objects', return_value=mock_objects):

        endpoint.get()
        assert endpoint.objects == mock_objects


def test_get_list_mixin_list_response(app):
    """assert the list_response method returns a valid response object.
    """

    endpoint = GetListEndpoint()
    mock_objects = [{'foo': 'bar'}]
    with mock.patch.object(GetListEndpoint, 'get_objects', return_value=mock_objects):

        resp = endpoint.get()
        assert resp.mimetype == 'application/json'
        assert 'Content-Type' in resp.headers
        assert resp.status_code == 200
        assert resp.data == b'{"payload": [{"foo": "bar"}]}'


def test_get_object_mixin_handle_get_request_none_not_allowed(app):
    """assert the GetObjectMixin handles raises a 404 when get_object returns none and
    allow none is false.
    """

    with mock.patch.object(CharacterEndpoint, 'get_object', return_value=None):
        endpoint = CharacterEndpoint()
        endpoint.allow_none = False
        with pytest.raises(NotFound):
            endpoint.get()


def test_get_object_mixin_handle_get_request_allow_none(app):
    """assert the GetObjectMixin handles no object correctly when allow_none=True
    """

    with mock.patch.object(CharacterEndpoint, 'get_object', return_value=None) as mock_method:
        endpoint = CharacterEndpoint()
        endpoint.allow_none = True
        resp = endpoint.get()
        assert mock_method.called
        assert resp.data.decode("utf-8") == '{"payload": null}'


def test_get_object_mixin_handle_get_request_get_object_not_defined(app):
    """assert the GetObjectMixin interface
    """

    class MyObjectEndpoint(Endpoint, GetObjectMixin):
        pass

    with pytest.raises(NotImplementedError):
        endpoint = MyObjectEndpoint()
        endpoint.get()


def test_get_object_mixin_handle_request_sets_response_attr(app):
    """Ensure that when the handle_get_request method is called the ResponseHandler is
    instantiated and set against the Endpoint.response attribute.
    """

    endpoint = CharacterEndpoint()
    endpoint.kwargs = {}
    endpoint.kwargs['obj_id'] = 1  # simulate dispatch_request being called.
    endpoint.get()
    assert isinstance(endpoint.response, ResponseHandler)


def test_get_object_mixin_sets_object(app):
    """Ensure obj param is set whenever a get request is handled by the mixin
    """

    endpoint = CharacterEndpoint()
    mock_object = {'foo': 'bar'}
    with mock.patch.object(CharacterEndpoint, 'get_object', return_value=mock_object):

        endpoint.get()
        assert endpoint.obj == mock_object


def test_get_object_mixin_obj_response(app):
    """assert the list_response method returns a valid response object.
    """

    endpoint = CharacterEndpoint()
    mock_object = {'foo': 'bar'}
    with mock.patch.object(CharacterEndpoint, 'get_object', return_value=mock_object):

        resp = endpoint.get()
        assert resp.mimetype == 'application/json'
        assert 'Content-Type' in resp.headers
        assert resp.status_code == 200
        assert resp.data == b'{"payload": {"foo": "bar"}}'


def test_create_mixin_response(app, client):

    endpoint = CharactersEndpoint()
    app.add_url_rule(
        '/characters',
        view_func=endpoint.as_view('characters'), methods=['POST']
    )
    resp = client.post(
        '/characters',
        data=json.dumps({'bar': 'baz'}),
        headers={'content-type': 'application/json'}
    )

    assert resp.status_code == 201
    assert resp.data == b'{"payload": {"bar": "baz"}}'


def test_create_mixin_sets_obj_from_request_handler(app, client):

    class MockRequstHandler(RequestHandler):

        def handle(self, data, **kwargs):
            return {'mock': True}

    class MyEndpoint(CharactersEndpoint):

        request_handler = MockRequstHandler

    endpoint = MyEndpoint()
    endpoint.post()

    assert endpoint.obj == {'mock': True}


def test_create_mixin_sets_request_handler(app):

    class MockRequstHandler(RequestHandler):

        def handle(self, data, **kwargs):
            return {'mock': True}

    class MyEndpoint(CharactersEndpoint):

        request_handler = MockRequstHandler

    endpoint = MyEndpoint()
    endpoint.post()

    assert isinstance(endpoint.request, MockRequstHandler)


def test_create_mixin_invalid_json(app, client):

    endpoint = CharactersEndpoint()
    app.add_url_rule(
        '/characters',
        view_func=endpoint.as_view('characters'), methods=['POST']
    )
    resp = client.post(
        '/characters',
        data='foo',
        headers={'content-type': 'application/json'}
    )

    assert resp.status_code == 400
    assert resp.data == b'{"message": "Invalid JSON data provided"}'


def test_create_mixin_calls_save_object(app):

    class MockRequstHandler(RequestHandler):

        def handle(self, data, **kwargs):
            return {'mock': True}

    class MyEndpoint(CharactersEndpoint):

        request_handler = MockRequstHandler

        def save_object(self, obj):

            obj['is_saved'] = True
            return obj

    endpoint = MyEndpoint()
    endpoint.post()
    assert 'is_saved' in endpoint.obj


def test_object_mixin_obj_property_calls_get_object():

    class MyEndpoint(Endpoint, ObjectMixin):
        pass

    with mock.patch.object(MyEndpoint, 'get_object', return_value={'foo': 'bar'}) as mocked:
        endpoint = MyEndpoint()
        endpoint.obj
        mocked.assert_called_once()


def test_object_mixin_obj_property_sets_obj():

    class MyEndpoint(Endpoint, ObjectMixin):
        pass

    with mock.patch.object(MyEndpoint, 'get_object', return_value={'foo': 'bar'}) as mocked:
        endpoint = MyEndpoint()
        endpoint.obj
        assert endpoint._obj == {'foo': 'bar'}


@PUT
def test_PUT_calls_handle_put_request(app):

    class MyEndpoint(CharacterEndpoint):

        def get_object(self):

            obj = {'foo': 'bar'}
            return obj

    with mock.patch.object(MyEndpoint, 'handle_put_request') as mock_handle_meth:
        endpoint = MyEndpoint()
        endpoint.put()
        mock_handle_meth.assert_called_once()


@PUT
def test_handle_PUT_request_calls_get_object(app):

    class MyEndpoint(CharacterEndpoint):

        def get_object(self):

            obj = {'foo': 'bar'}
            return obj

    with mock.patch.object(MyEndpoint, 'get_object', return_value={'foo': 'bar'}) as mock_get_object:
        endpoint = MyEndpoint()
        endpoint.put()
        mock_get_object.assert_called_once()


@PUT
def test_PUT_mixin_sets_request_handler(app):

    class MockRequstHandler(RequestHandler):

        def handle(self, data, **kwargs):
            return {'mock': True}

    class MyEndpoint(CharacterEndpoint):

        request_handler = MockRequstHandler

        def get_object(self):

            obj = {'foo': 'bar'}
            return obj

    endpoint = MyEndpoint()
    endpoint.put()

    assert isinstance(endpoint.request, MockRequstHandler)


@PUT
def test_handle_PUT_request_calls_update_object(app):

    class MyEndpoint(CharacterEndpoint):

        def get_object(self):

            obj = {'foo': 'bar'}
            return obj

    with mock.patch.object(MyEndpoint, 'update_object') as mock_update_object:
        endpoint = MyEndpoint()
        endpoint.put()
        mock_update_object.assert_called_once()


@PUT
def test_PUT_request_response(app):

    class MyEndpoint(CharacterEndpoint):

        def get_object(self):

            obj = {'foo': 'bar'}
            return obj

    endpoint = MyEndpoint()
    resp = endpoint.put()
    assert resp.status_code == 200
    assert resp.data == b'{"payload": {"foo": "bar"}}'


@DELETE
def test_DELETE_calls_handle_delete_request(app):

    class MyEndpoint(CharacterEndpoint):

        def get_object(self):

            obj = {'foo': 'bar'}
            return obj

    with mock.patch.object(MyEndpoint, 'handle_delete_request') as mock_handle_meth:
        endpoint = MyEndpoint()
        endpoint.delete()
        mock_handle_meth.assert_called_once()


@DELETE
def test_handle_DELETE_request_calls_get_object(app):

    class MyEndpoint(CharacterEndpoint):

        def get_object(self):

            obj = {'foo': 'bar'}
            return obj

    with mock.patch.object(MyEndpoint, 'get_object') as mock_get_object:
        endpoint = MyEndpoint()
        endpoint.delete()
        mock_get_object.assert_called_once()


@DELETE
def test_handle_DELETE_request_calls_delete_object(app):

    class MyEndpoint(CharacterEndpoint):

        def get_object(self):

            obj = {'foo': 'bar'}
            return obj

    with mock.patch.object(MyEndpoint, 'delete_object') as mock_delete_object:
        endpoint = MyEndpoint()
        endpoint.delete()
        mock_delete_object.assert_called_once_with({'foo': 'bar'})


@DELETE
def test_handle_DELETE_request_response(app):

    class MyEndpoint(CharacterEndpoint):

        def get_object(self):

            obj = {'foo': 'bar'}
            return obj

    endpoint = MyEndpoint()
    resp = endpoint.delete()
    assert resp.status_code == 204
    assert resp.data == b''
