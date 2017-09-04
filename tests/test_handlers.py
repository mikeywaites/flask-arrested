import pytest
import json

from mock import patch

from werkzeug.exceptions import BadRequest
from arrested import (
    Handler, Endpoint, ResponseHandler,
    RequestHandler, JSONRequestMixin, JSONResponseMixin)


def test_handler_params_set():

    endpoint = Endpoint()
    handler = Handler(endpoint, payload_key='foo', **{'test': 'foo'})
    assert handler.endpoint == endpoint
    assert handler.payload_key == 'foo'
    assert handler.params == {'test': 'foo'}


def test_handler_handle_method_basic():
    """By default the hanlde method simply returns the data passed to it.
    """

    endpoint = Endpoint()
    handler = Handler(endpoint)
    resp = handler.handle({'foo': 'bar'})
    assert resp == {'foo': 'bar'}


def test_handler_process_method_calls_handle():

    endpoint = Endpoint()
    handler = Handler(endpoint)
    with patch.object(Handler, 'handle') as _mock:
        handler.process({'foo': 'bar'})
        _mock.assert_called_once_with({'foo': 'bar'})


def test_handler_process_method_response():

    endpoint = Endpoint()
    handler = Handler(endpoint)
    resp = handler.process({'foo': 'bar'})
    assert resp == handler
    assert resp.data == {'foo': 'bar'}


def test_response_handler_handle_method(app):

    endpoint = Endpoint()
    handler = ResponseHandler(endpoint)
    with app.test_request_context('/test', method='GET'):
        resp = handler.process({'foo': 'bar'})
        assert resp == handler
        assert resp.data == {'foo': 'bar'}


def test_response_handler_get_response_data(app):

    endpoint = Endpoint()
    handler = ResponseHandler(endpoint)
    with app.test_request_context('/test', method='GET'):
        resp = handler.process({'foo': 'bar'})
        assert resp == handler
        assert resp.data == {'foo': 'bar'}


def test_request_handler_handle_method():

    endpoint = Endpoint()
    handler = RequestHandler(endpoint)
    # as we're passing data directly to process() the get_request_data() method will not
    # be called so the incoming data is not required to be in JSON format.
    resp = handler.process({'foo': 'bar'})
    assert resp == handler
    assert resp.data == {'foo': 'bar'}


def test_request_handler_handle_method_request_data(app):

    endpoint = Endpoint()
    handler = RequestHandler(endpoint)
    with app.test_request_context(
            '/test',
            data=json.dumps({'foo': 'bar'}),
            headers={'content-type': 'application/json'},
            method='POST'):

        resp = handler.process()
        assert resp == handler
        assert resp.data == {'foo': 'bar'}


def test_json_request_mixin_valid_json_request(app):

    mixin = JSONRequestMixin()
    with app.test_request_context(
            '/test',
            data=json.dumps({'foo': 'bar'}),
            headers={'content-type': 'application/json'},
            method='POST'):

        resp = mixin.get_request_data()
        assert resp == {'foo': 'bar'}


def test_json_request_mixin_invalid_json(app):

    endpoint = Endpoint()
    mixin = JSONRequestMixin()
    mixin.endpoint = endpoint
    with app.test_request_context(
            '/test',
            data=b'not valid',
            headers={'content-type': 'application/json'},
            method='POST'):

        with pytest.raises(BadRequest):
            mixin.get_request_data()


def test_json_response_mixin(app):

    mixin = JSONResponseMixin()
    mixin.payload_key = 'data'
    mixin.data = {'foo': 'bar'}
    assert mixin.get_response_data() == json.dumps({"data": {"foo": "bar"}})
