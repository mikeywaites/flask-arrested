import json

from mock import patch, MagicMock

from flask import Response
from werkzeug.exceptions import HTTPException
from arrested import (
    ArrestedAPI,
    Resource,
    Endpoint,
    ResponseHandler,
    GetListMixin,
    CreateMixin,
    PutObjectMixin,
    PatchObjectMixin,
)

from tests.utils import assertResponse


def test_get_endpoint_name():
    """test that user specified names are used by the get_name method
    """

    class MyEndpoint(Endpoint):
        name = "test"

    endpoint = MyEndpoint()
    assert endpoint.get_name() == "test"


def test_get_endpoint_name_defaults_to_class_name():
    """test the endpoint name will default to the classname if no custom name is provided
    """

    class MyEndpoint(Endpoint):
        name = None

    endpoint = MyEndpoint()
    assert endpoint.get_name() == "myendpoint"


def test_make_response():
    """Test the default response returned by make_response method
    """

    data = json.dumps({"foo": "bar"})
    resp = Endpoint().make_response(data)
    exp_resp = Response(
        response=data, headers=None, mimetype="application/json", status=200
    )
    assertResponse(resp, exp_resp)


def test_make_response_set_mimetype():
    """test make response with a specific mimetype param passed to make_response method
    """

    data = json.dumps({"foo": "bar"})
    resp = Endpoint().make_response(data, mime="text/html")
    exp_resp = Response(response=data, headers=None, mimetype="text/html", status=200)
    assertResponse(resp, exp_resp)


def test_make_response_set_headers():
    """Test make_response with custom headers
    """
    data = json.dumps({"foo": "bar"})
    resp = Endpoint().make_response(data, headers={"Cache-Control": "must-revalidate"})
    exp_resp = Response(
        response=data,
        headers={"Cache-Control": "must-revalidate"},
        mimetype="application/json",
        status=200,
    )
    assertResponse(resp, exp_resp)


def test_make_response_set_status():
    """Test make_response with no default status code
    """
    data = json.dumps({"foo": "bar"})
    resp = Endpoint().make_response(data, status=201)
    exp_resp = Response(
        response=data, headers=None, mimetype="application/json", status=201
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
            params["mapper_class"] = FakeMapper

            return params

    handler = MyEndpoint().get_response_handler()
    assert isinstance(handler, ResponseHandler)
    assert handler.params == {"mapper_class": FakeMapper}


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
        endpoint.return_error(400, payload={"error": True})
    except HTTPException as resp:
        assert resp.code == 400
        assert resp.response.data == b'{"error": true}'


def test_endpoint_dispatch_request_method_not_allowed_returns_error(app):
    class MyEndpoint(Endpoint, GetListMixin):

        methods = ["GET"]

        def handle_get_request(self):
            pass

    with patch.object(MyEndpoint, "return_error") as mock_return_error:

        with app.test_request_context("/test", method="POST"):
            MyEndpoint().dispatch_request()

            mock_return_error.assert_called_once_with(405)


def test_get_calls_handle_get_request():
    class MyEndpoint(Endpoint):
        def handle_get_request(self):
            pass

    data = {"foo": "bar"}
    with patch.object(MyEndpoint, "handle_get_request", return_value=data) as mocked:
        MyEndpoint().get()
        mocked.assert_called_once()


def test_post_calls_handle_post_request():
    class MyEndpoint(Endpoint):
        def handle_post_request(self):
            pass

    data = {"foo": "bar"}
    with patch.object(MyEndpoint, "handle_post_request", return_value=data) as _mock:
        MyEndpoint().post()
        _mock.assert_called_once()


def test_put_calls_handle_put_request():
    class MyEndpoint(Endpoint):
        def handle_put_request(self):
            pass

    data = {"foo": "bar"}
    with patch.object(MyEndpoint, "handle_put_request", return_value=data) as _mock:
        MyEndpoint().put()
        _mock.assert_called_once()


def test_patch_calls_handle_patch_request():
    class MyEndpoint(Endpoint):
        def handle_patch_request(self):
            pass

    data = {"foo": "bar"}
    with patch.object(MyEndpoint, "handle_patch_request", return_value=data) as _mock:
        MyEndpoint().patch()
        _mock.assert_called_once()


def test_endpoint_dispatch_request_method_calls_process_before_request_hooks(app):
    class MyEndpoint(Endpoint, GetListMixin):

        methods = ["GET"]

        def handle_get_request(self):
            pass

    with patch.object(Endpoint, "process_before_request_hooks") as mock_before_hooks:
        MyEndpoint().dispatch_request()
        mock_before_hooks.assert_called_once_with()


def test_endpoint_dispatch_request_method_calls_process_after_request_hooks(app):

    mock_response = MagicMock(spec=Response)

    class MyEndpoint(Endpoint, GetListMixin):

        methods = ["GET"]

        def handle_get_request(self):
            return mock_response

    with patch.object(Endpoint, "process_after_request_hooks") as mock_after_hooks:
        MyEndpoint().dispatch_request()
        mock_after_hooks.assert_called_once_with(mock_response)


def test_process_before_request_hooks_processed_in_order(app):

    call_sequence = []

    def test_hook(type_, sequence):
        def hook(endpoint):
            sequence.append(type_)

        return hook

    api_hook = test_hook("api", call_sequence)
    resource_hook = test_hook("resource", call_sequence)
    endpoint_hook = test_hook("endpoint", call_sequence)
    endpoint_get_hook = test_hook("endpoint_get", call_sequence)

    my_api = ArrestedAPI(before_all_hooks=[api_hook], url_prefix="/")
    my_api.init_app(app)
    my_resource = Resource("test", __name__, before_all_hooks=[resource_hook])

    class MyEndpoint(Endpoint):

        before_all_hooks = [endpoint_hook]
        before_get_hooks = [endpoint_get_hook]
        url = ""

    my_resource.add_endpoint(Endpoint)
    my_api.register_resource(my_resource)
    endpoint = MyEndpoint()
    endpoint.resource = my_resource
    endpoint.meth = "get"

    endpoint.process_before_request_hooks()

    assert call_sequence == ["api", "resource", "endpoint", "endpoint_get"]


def test_process_before_hooks_no_resource(app):

    log_request = MagicMock(return_value=None)

    class MyEndpoint(Endpoint, GetListMixin):

        before_get_hooks = [log_request]

        def get_objects(self):
            return [{"foo": "bar"}]

    endpoint = MyEndpoint()
    endpoint.resource = None
    endpoint.meth = "get"

    endpoint.process_before_request_hooks()
    log_request.assert_called_once()


def test_process_before_hooks_request_meth_not_handled(app):

    log_request = MagicMock(return_value=None)

    class MyEndpoint(Endpoint, GetListMixin):

        before_get_hooks = [log_request]

        def get_objects(self):
            return [{"foo": "bar"}]

    endpoint = MyEndpoint()
    endpoint.resource = None
    endpoint.meth = "options"

    endpoint.process_before_request_hooks()
    assert not log_request.called


def test_process_after_request_hooks_processed_in_order(app):

    call_sequence = []

    def test_hook(type_, sequence):
        def hook(endpoint, resp):
            sequence.append(type_)

        return hook

    api_hook = test_hook("api", call_sequence)
    resource_hook = test_hook("resource", call_sequence)
    endpoint_hook = test_hook("endpoint", call_sequence)
    endpoint_get_hook = test_hook("endpoint_get", call_sequence)

    my_api = ArrestedAPI(after_all_hooks=[api_hook], url_prefix="/")
    my_api.init_app(app)
    my_resource = Resource("test", __name__, after_all_hooks=[resource_hook])

    class MyEndpoint(Endpoint):

        after_all_hooks = [endpoint_hook]
        after_get_hooks = [endpoint_get_hook]
        url = ""

    my_resource.add_endpoint(Endpoint)
    my_api.register_resource(my_resource)
    endpoint = MyEndpoint()
    endpoint.resource = my_resource
    endpoint.meth = "get"

    resp = MagicMock(spec=Response())
    endpoint.process_after_request_hooks(resp)

    assert call_sequence == ["endpoint_get", "endpoint", "resource", "api"]


def test_process_after_hooks_no_resource(app):

    log_request = MagicMock(return_value=None)

    class MyEndpoint(Endpoint, GetListMixin):

        after_get_hooks = [log_request]

        def get_objects(self):
            return [{"foo": "bar"}]

    endpoint = MyEndpoint()
    endpoint.resource = None
    endpoint.meth = "get"

    resp = MagicMock(spec=Response())
    endpoint.process_after_request_hooks(resp)
    log_request.assert_called_once()


def test_process_after_hooks_request_meth_not_handled(app):

    log_request = MagicMock(return_value=None)

    class MyEndpoint(Endpoint, GetListMixin):

        after_get_hooks = [log_request]

        def get_objects(self):
            return [{"foo": "bar"}]

    endpoint = MyEndpoint()
    endpoint.resource = None
    endpoint.meth = "options"

    resp = MagicMock(spec=Response())
    endpoint.process_after_request_hooks(resp)
    assert not log_request.called


def test_delete_calls_handle_delete_request():
    pass


def test_restrict_methods():
    pass


def test_endpoint_url():
    pass
