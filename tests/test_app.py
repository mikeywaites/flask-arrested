import pytest

from flask import url_for
from arrested import Arrested


from .fixtures import TestResource


def test_api_object_instantiation_with_flask_object(flask_app):
    """Create a new :py:class:`arrested.app.Arrested` instance passing the flask
    app object directly to the contstructor
    """

    api = Arrested(flask_app)
    assert api.app is flask_app


def test_api_object_instantiation_deferred_flask_app(flask_app):
    """Create a new :py:class:`arrested.app.Arrested` ensuring that flask_app
    can be set later using :meth:`api.init_app`
    """

    api = Arrested()
    api.init_app(flask_app)
    assert api.app is flask_app


def test_api_object_custom_name(flask_app):
    """Create a new :py:class:`arrested.app.Arrested` providing a user defined
    api name.
    """

    api = Arrested(name='my_api')
    api.init_app(flask_app)
    assert api.name == 'my_api'


def test_api_object_url_prefix(flask_app):
    """Create a new :py:class:`arrested.app.Arrested` providing a user defined
    api url_prefix
    """

    api = Arrested(url_prefix='/v1.1')
    api.init_app(flask_app)
    assert api.url_prefix == '/v1.1'


def test_api_object_no_url_prefix(flask_app):
    """Create a new :py:class:`arrested.app.Arrested` providing a user defined
    api url_prefix
    """

    api = Arrested(url_prefix=None)
    api.init_app(flask_app)
    assert api.url_prefix is None
    assert api.get_api_url(url='/foo') == '/foo'


def test_api_object_register_resource_no_app(flask_app):
    """Ensure that :meth:`Arrested.register` requries that the Arrested instance has
    been intialised with a flask app instance.
    """

    api = Arrested()
    with pytest.raises(AssertionError):
        api.register(TestResource)


def test_register_endpoint_with_url_override(flask_app):
    """"provide Arrested.regsister with a customer url and ensure the resource
    is mapped using the custom url.
    """

    api = Arrested(flask_app)
    api.register(TestResource,  url='/foo')
    url = url_for('api.test_resource')

    assert url == '/v1/foo'


def test_register_endpoint(flask_app):
    """"provide Arrested.regsister no url and ensure the Resource.url is used
    is mapped using the custom url.
    """

    api = Arrested(flask_app)
    api.register(TestResource)
    url = url_for('api.test_resource')

    assert url == '/v1/test'
