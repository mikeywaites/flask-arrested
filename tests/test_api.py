from flask import url_for

from arrested import ArrestedAPI, Resource, Endpoint


def initialise_app_via_constructor(app):
    """Test instantiating ArrestedAPI obj passing flask app object directly
    """

    api_v1 = ArrestedAPI(app)
    assert api_v1.app == app


def defer_app_initialisation(app):
    """Test deferring initialising the flask app object using init_app method.
    """
    api_v1 = ArrestedAPI()
    api_v1.init_app(app)
    assert api_v1.app == app


def test_register_resource(app):
    """Test that Resources are properly reigstered as a blueprint when
    ArrestedAPI.register_resource is called.
    """
    api_v1 = ArrestedAPI(app)
    example_resource = Resource('example', __name__, url_prefix='/example')
    api_v1.register_resource(example_resource)
    assert app.blueprints == {'example': example_resource}


def test_register_all(app):
    """Test that Resources are properly reigstered as a blueprint when
    ArrestedAPI.register_resource is called.
    """
    api_v1 = ArrestedAPI(app)
    example_resource = Resource('example', __name__, url_prefix='/example')
    example_resource_2 = Resource('example_2', __name__, url_prefix='/example-2')
    api_v1.register_all([example_resource, example_resource_2])
    assert app.blueprints == {
        'example': example_resource,
        'example_2': example_resource_2
    }


def test_defer_resource_registration(app):
    """Test that Resources are properly reigstered as a blueprint when
    ArrestedAPI.register_resource is called.
    """
    api_v1 = ArrestedAPI()
    example_resource = Resource('example', __name__, url_prefix='/example')
    example_resource_2 = Resource('example_2', __name__, url_prefix='/example-2')
    api_v1.register_resource(example_resource, defer=True)
    api_v1.register_resource(example_resource_2, defer=True)

    assert app.blueprints == {}

    api_v1.init_app(app)
    assert app.blueprints == {
        'example': example_resource,
        'example_2': example_resource_2
    }


def test_register_resource_with_url_prefix(app):
    """Test that the url_prefix is correctly applied to all resources when provided
    """
    api_v1 = ArrestedAPI(app, url_prefix='/v1')
    example_resource = Resource('example', __name__, url_prefix='/example')

    class MyEndpoint(Endpoint):

        name = 'test'

    example_resource.add_endpoint(MyEndpoint)
    api_v1.register_resource(example_resource)

    assert url_for('example.test') == '/v1/example'


def test_api_request_middleware(app, client):
    evts = []

    def api_before_func(*args, **kwarsg):
        evts.append('api_before')
        return None

    def api_after_func(endpoint, response):
        response.data += b'|api_after'
        evts.append('api_after')
        return response

    def resource_before_func(endpoint):
        evts.append('resource_before')
        return None

    def resource_after_func(endpoint, response):
        response.data += b'|resource_after'
        evts.append('resource_after')
        return response

    api_v1 = ArrestedAPI(
        app,
        url_prefix='/v1',
        before_all_hooks=[api_before_func],
        after_all_hooks=[api_after_func]
    )
    example_resource = Resource(
        'example', __name__,
        url_prefix='/example',
        before_all_hooks=[resource_before_func],
        after_all_hooks=[resource_after_func]
    )

    class MyEndpoint(Endpoint):

        name = 'test'

        def get(self, *args, **kwargs):

            assert 'api_before' in evts
            assert 'api_after' not in evts
            assert 'resource_before' in evts
            assert 'resource_after' not in evts
            return 'request'

    example_resource.add_endpoint(MyEndpoint)
    api_v1.register_resource(
        example_resource,
    )

    resp = client.get(url_for('example.test'))
    assert resp.data == b'request|resource_after|api_after'
    assert evts == ['api_before', 'resource_before', 'resource_after', 'api_after']


def test_api_request_middleware_limited_to_api(app, client):
    evts = []

    def api_before_func(*args, **kwarsg):
        evts.append('api_before')
        return None

    def api_after_func(endpoint, response):
        response.data += b'|api_after'
        evts.append('api_after')
        return response

    def resource_before_func(endpoint):
        evts.append('resource_before')
        return None

    def resource_after_func(endpoint, response):
        response.data += b'|resource_after'
        evts.append('resource_after')
        return response

    api_v1 = ArrestedAPI(
        app,
        url_prefix='/v1',
        before_all_hooks=[api_before_func],
        after_all_hooks=[api_after_func]
    )
    api_v2 = ArrestedAPI(
        app,
        url_prefix='/v2',
    )
    example_resource = Resource(
        'example', __name__,
        url_prefix='/example',
        before_all_hooks=[resource_before_func],
        after_all_hooks=[resource_after_func]
    )
    example2_resource = Resource(
        'example2', __name__,
        url_prefix='/example2'
    )

    class MyEndpoint(Endpoint):

        name = 'test'

        def get(self, *args, **kwargs):

            assert 'api_before' not in evts
            assert 'api_after' not in evts
            assert 'resource_before' not in evts
            assert 'resource_after' not in evts
            return 'request'

    example_resource.add_endpoint(MyEndpoint)
    example2_resource.add_endpoint(MyEndpoint)
    api_v1.register_resource(
        example_resource,
    )
    api_v2.register_resource(
        example2_resource,
    )

    resp = client.get(url_for('example2.test'))
    assert resp.data == b'request'
