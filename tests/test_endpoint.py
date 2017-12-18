import json

from mock import patch, MagicMock

from flask import Response
from werkzeug.exceptions import HTTPException
from arrested import (
    Endpoint, ResponseHandler, GetListMixin,
    CreateMixin, PutObjectMixin, PatchObjectMixin
)

from tests.utils import assertResponse


def test_get_endpoint_name():
    """test that user specified names are used by the get_name method
    """

    class MyEndpoint(Endpoint):
        name = 'test'

    endpoint = MyEndpoint()
    assert endpoint.get_name() == 'test'


def test_get_endpoint_name_defaults_to_class_name():
    """test the endpoint name will default to the classname if no custom name is provided
    """

    class MyEndpoint(Endpoint):
        name = None

    endpoint = MyEndpoint()
    assert endpoint.get_name() == 'myendpoint'


def test_make_response():
    """Test the default response returned by make_response method
    """

    data = json.dumps({'foo': 'bar'})
    resp = Endpoint().make_response(data)
    exp_resp = Response(
        response=data,
        headers=None,
        mimetype='application/json',
        status=200
    )
    assertResponse(resp, exp_resp)


def test_make_response_set_mimetype():
    """test make response with a specific mimetype param passed to make_response method
    """

    data = json.dumps({'foo': 'bar'})
    resp = Endpoint().make_response(data, mime='text/html')
    exp_resp = Response(
        response=data,
        headers=None,
        mimetype='text/html',
        status=200
    )
    assertResponse(resp, exp_resp)


def test_make_response_set_headers():
    """Test make_response with custom headers
    """
    data = json.dumps({'foo': 'bar'})
    resp = Endpoint().make_response(data, headers={'Cache-Control': 'must-revalidate'})
    exp_resp = Response(
        response=data,
        headers={'Cache-Control': 'must-revalidate'},
        mimetype='application/json',
        status=200
    )
    assertResponse(resp, exp_resp)


def test_make_response_set_status():
    """Test make_response with no default status code
    """
    data = json.dumps({'foo': 'bar'})
    resp = Endpoint().make_response(data, status=201)
    exp_resp = Response(
        response=data,
        headers=None,
        mimetype='application/json',
        status=201
    )
    assertResponse(resp, exp_resp)


def test_get_response_handler_with_custom_handler_params():
    """test get_response_handler method is passed custom params when
    get_response_handler_params is overridden
    """

    class FakeMapper(object):
        pass


    class MyEndpoint(Endpoint):

        def get_response_handler_params(self, **params):

            params = super(MyEndpoint, self).get_response_handler_params(**params)
            params['mapper_class'] = FakeMapper

            return params

    handler = MyEndpoint().get_response_handler()
    assert isinstance(handler, ResponseHandler)
    assert handler.params == {'mapper_class': FakeMapper}


def test_get_response_handler_custom_handler():

    class MyResponseHandler(ResponseHandler):
        pass

    class MyEndpoint(Endpoint):

        response_handler = MyResponseHandler

    handler = MyEndpoint().get_response_handler()
    assert isinstance(handler, MyResponseHandler)


def test_get_request_handler():
    pass


def test_get_request_handler_custom_handler():
    pass


def test_return_error_response():
    endpoint = Endpoint()
    try:
        endpoint.return_error(400, payload={'error': True})
    except HTTPException as resp:
        assert resp.code == 400
        assert resp.response.data == b'{"error": true}'


def test_return_error_response_with_headers():
    endpoint = Endpoint()
    try:
        endpoint.return_error(400, payload={'error': True}, headers={'X-Test': 'foo'})
    except HTTPException as resp:
        assert resp.response.headers['X-Test'] == 'foo'


def test_return_error_response_as_json_false():
    """Ensure that when as_json=False is passed to return_error that the method will
    not attempt to serialize the provided payload to JSON
    """
    endpoint = Endpoint()
    payload = json.dumps({'error': True})
    try:
        endpoint.return_error(
            400,
            payload=payload,
            as_json=False,
            headers={'X-Test': 'foo'}
        )
    except HTTPException as resp:
        assert resp.response.headers['X-Test'] == 'foo'


def test_return_error_default_content_type():
    """ensure that the default content type returned with the response is application/json
    """
    endpoint = Endpoint()
    try:
        endpoint.return_error(
            400,
            payload={'error': True},
        )
    except HTTPException as resp:
        assert resp.response.headers['Content-Type'] == 'application/json'


def test_return_error_custom_content_type():
    """ensure that the a custom content type returned with the
    response is application/json
    """
    endpoint = Endpoint()
    payload = b'<html><body>Error</body></html>'
    try:
        endpoint.return_error(
            400,
            payload=payload,
            content_type='text/html',
            as_json=False
        )
    except HTTPException as resp:
        assert resp.response.data == payload


def test_get_calls_handle_get_request():
    class MyEndpoint(Endpoint):

        def handle_get_request(self):
            pass

    data = {'foo': 'bar'}
    with patch.object(MyEndpoint, 'handle_get_request', return_value=data) as mocked:
        MyEndpoint().get()
        mocked.assert_called_once()


def test_before_get_hooks(app):

    log_request = MagicMock(return_value=None)

    class MyEndpoint(Endpoint, GetListMixin):

        before_get_hooks = [log_request, ]

        def get_objects(self):
            return [{'foo': 'bar'}]

    MyEndpoint().dispatch_request()
    log_request.assert_called_once()


def test_after_get_hooks(app):

    def set_headers(endpoint, response):
        response.headers.add('X-Test', 1)
        return response

    class MyEndpoint(Endpoint, GetListMixin):

        after_get_hooks = [set_headers]

        def get_objects(self):
            return [{'foo': 'bar'}]

    resp = MyEndpoint().dispatch_request()
    assert 'X-Test' in resp.headers


def test_post_calls_handle_post_request():
    class MyEndpoint(Endpoint):

        def handle_post_request(self):
            pass

    data = {'foo': 'bar'}
    with patch.object(MyEndpoint, 'handle_post_request', return_value=data) as _mock:
        MyEndpoint().post()
        _mock.assert_called_once()


def test_before_post_hooks(app):

    log_request = MagicMock(return_value=None)

    class MyEndpoint(Endpoint, CreateMixin):

        before_post_hooks = [log_request, ]

        def save_object(self, obj):
            return obj

    with app.test_request_context('/test', method='POST'):
        MyEndpoint().dispatch_request()
        log_request.assert_called_once()


def test_after_post_hooks(app):

    def set_headers(endpoint, response):
        response.headers.add('X-Test', 1)
        return response

    class MyEndpoint(Endpoint, CreateMixin):

        after_post_hooks = [set_headers]

        def save_object(self, obj):
            return obj

    with app.test_request_context('/test', method='POST'):
        resp = MyEndpoint().dispatch_request()
        assert 'X-Test' in resp.headers


def test_put_calls_handle_put_request():
    class MyEndpoint(Endpoint):

        def handle_put_request(self):
            pass

    data = {'foo': 'bar'}
    with patch.object(MyEndpoint, 'handle_put_request', return_value=data) as _mock:
        MyEndpoint().put()
        _mock.assert_called_once()


def test_before_put_hooks(app):

    log_request = MagicMock(return_value=None)

    class MyEndpoint(Endpoint, PutObjectMixin):

        before_put_hooks = [log_request, ]

        def get_object(self):

            return {'foo': 'bar'}

        def update_object(self, obj):
            return obj

    with app.test_request_context('/test', method='PUT'):
        MyEndpoint().dispatch_request()
        log_request.assert_called_once()


def test_after_put_hooks(app):

    def set_headers(endpoint, response):
        response.headers.add('X-Test', 1)
        return response

    class MyEndpoint(Endpoint, PutObjectMixin):

        after_put_hooks = [set_headers]

        def get_object(self):

            return {'foo': 'bar'}

        def update_object(self, obj):
            return obj

    with app.test_request_context('/test', method='PUT'):
        resp = MyEndpoint().dispatch_request()
        assert 'X-Test' in resp.headers


def test_patch_calls_handle_patch_request():
    class MyEndpoint(Endpoint):

        def handle_patch_request(self):
            pass

    data = {'foo': 'bar'}
    with patch.object(MyEndpoint, 'handle_patch_request', return_value=data) as _mock:
        MyEndpoint().patch()
        _mock.assert_called_once()


def test_before_patch_hooks(app):

    log_request = MagicMock(return_value=None)

    class MyEndpoint(Endpoint, PatchObjectMixin):

        before_patch_hooks = [log_request, ]

        def get_object(self):

            return {'foo': 'bar'}

        def patch_object(self, obj):
            return obj

    with app.test_request_context('/test', method='PATCH'):
        MyEndpoint().dispatch_request()
        log_request.assert_called_once()


def test_after_patch_hooks(app):

    def set_headers(endpoint, response):
        response.headers.add('X-Test', 1)
        return response

    class MyEndpoint(Endpoint, PatchObjectMixin):

        after_patch_hooks = [set_headers]

        def get_object(self):

            return {'foo': 'bar'}

        def patch_object(self, obj):
            return obj

    with app.test_request_context('/test', method='PATCH'):
        resp = MyEndpoint().dispatch_request()
        assert 'X-Test' in resp.headers


def test_delete_calls_handle_delete_request():
    pass


def test_restrict_methods():
    pass


def test_endpoint_url():
    pass
