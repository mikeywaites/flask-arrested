import json

from unittest.mock import MagicMock

from flask import url_for
from arrested import Resource, ArrestedAPI, Endpoint
from tests.endpoints import (
    CharactersEndpoint,
    CharacterEndpoint,
    PlanetsEndpoint,
    _get_character_objects, _get_planet_objects
)


def test_set_resource_url_prefix(api_v1):
    cr = Resource('characters', __name__, url_prefix='/characters')
    assert cr.url_prefix == '/characters'


def test_set_resource_name():

    cr = Resource('characters', __name__, url_prefix='/characters')
    assert cr.name == 'characters'


def test_set_add_resource_url_for(api_v1, client):

    characters_resource = Resource('characters', __name__, url_prefix='/characters')
    characters_resource.add_endpoint(CharactersEndpoint)
    api_v1.register_resource(characters_resource)

    url = url_for('characters.list')
    assert url == '/v1/characters'


def test_set_add_resource_endpoint_with_prefix(api_v1, client):

    characters_resource = Resource('characters', __name__, url_prefix='/characters')
    characters_resource.add_endpoint(CharactersEndpoint)
    api_v1.register_resource(characters_resource)

    resp = client.get('/v1/characters')

    assert resp.data == bytes(
        json.dumps({'payload': _get_character_objects()}).encode('utf-8')
    )


def test_set_add_resource_endpoint_with_no_prefix(api_v1, client):

    characters_resource = Resource('characters', __name__)

    class JedisEndpoint(CharactersEndpoint):
        url = '/jedis'

        def get_objects(self):

            return [_get_character_objects()[1]]

    characters_resource.add_endpoint(JedisEndpoint)
    api_v1.register_resource(characters_resource)

    resp = client.get('/v1/jedis')

    assert resp.data == bytes(
        json.dumps({'payload': [_get_character_objects()[1]]}).encode('utf-8')
    )


def test_set_add_resource_endpoint_with_url_params(api_v1, client):

    characters_resource = Resource('characters', __name__, url_prefix='/jedis')

    class JediObjectEndpoint(CharacterEndpoint):
        url = '/<string:obj_id>'

        def get_object(self):

            return _get_character_objects()[1]

    characters_resource.add_endpoint(JediObjectEndpoint)
    api_v1.register_resource(characters_resource)

    resp = client.get('/v1/jedis/1')

    assert resp.data == bytes(
        json.dumps({'payload': _get_character_objects()[1]}).encode('utf-8')
    )


def test_set_add_resource_endpoint_with_no_api_prefix(app, client):

    api = ArrestedAPI(app)
    characters_resource = Resource('characters', __name__, url_prefix='/characters')

    characters_resource.add_endpoint(CharactersEndpoint)
    api.register_resource(characters_resource)

    resp = client.get('/characters')

    assert resp.data == bytes(
        json.dumps({'payload': _get_character_objects()}).encode('utf-8')
    )


def test_set_add_multiple_resources_with_no_api_prefix(app, client):

    api = ArrestedAPI(app)
    characters_resource = Resource('characters', __name__, url_prefix='/characters')
    planets_resource = Resource('planets', __name__, url_prefix='/planets')

    characters_resource.add_endpoint(CharactersEndpoint)
    planets_resource.add_endpoint(PlanetsEndpoint)

    api.register_resource(characters_resource)
    api.register_resource(planets_resource)

    resp = client.get('/characters')
    assert resp.data == bytes(
        json.dumps({'payload': _get_character_objects()}).encode('utf-8')
    )

    resp = client.get('/planets')
    assert resp.data == bytes(
        json.dumps({'payload': _get_planet_objects()}).encode('utf-8')
    )


def test_resource_before_request_middleware(app, client):

    api = ArrestedAPI(app)
    log_request = MagicMock(return_value=None)
    characters_resource = Resource(
        'characters',
        __name__,
        url_prefix='/characters',
        before_all_hooks=[log_request]
    )

    characters_resource.add_endpoint(CharactersEndpoint)

    api.register_resource(characters_resource)

    client.get('/characters')
    assert log_request.called


def test_resource_after_request_middleware(app, client):

    log_request = MagicMock(return_value=None)

    def log_middleware(endpoint, response):
        log_request()
        return response

    api = ArrestedAPI(app)
    characters_resource = Resource(
        'characters',
        __name__,
        url_prefix='/characters',
        after_all_hooks=[log_middleware]
    )

    characters_resource.add_endpoint(CharactersEndpoint)

    api.register_resource(characters_resource)

    client.get('/characters')
    assert log_request.called


def test_middleware_only_applied_to_resources_endpoints(app, client):

    log_request = MagicMock(return_value=None)

    def log_middleware(endpoint, response):
        log_request()
        return response

    api = ArrestedAPI(app)
    characters_resource = Resource(
        'characters',
        __name__,
        url_prefix='/characters',
        after_all_hooks=[log_middleware]
    )
    planets_resource = Resource('planets', __name__, url_prefix='/planets')

    characters_resource.add_endpoint(CharactersEndpoint)
    planets_resource.add_endpoint(PlanetsEndpoint)

    api.register_resource(characters_resource)
    api.register_resource(planets_resource)

    client.get('/characters')
    assert log_request.call_count == 1
    client.get('/planets')
    assert log_request.call_count == 1
