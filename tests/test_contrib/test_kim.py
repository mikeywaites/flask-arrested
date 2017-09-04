import pytest

from kim import Mapper, field

from werkzeug.exceptions import BadRequest, UnprocessableEntity
from mock import MagicMock

from arrested import PutObjectMixin, PatchObjectMixin
from arrested.contrib.kim_arrested import (
    KimHandler, KimResponseHandler,
    KimRequestHandler,
    KimEndpoint
)

from tests.endpoints import CharactersEndpoint


class MyObject(object):

    def __init__(self, id=None, name=''):

        self.id = id
        self.name = name

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class MyMapper(Mapper):

    __type__ = MyObject

    id = field.Integer()
    name = field.String()

    __roles__ = {
        'name_only': ['name']
    }


def test_kim_invalid_mapper_class():
    with pytest.raises(Exception):
        endpoint = CharactersEndpoint()
        KimHandler(endpoint, mapper_class=None).mapper


def test_kim_handler_get_mapper():

    endpoint = CharactersEndpoint()
    handler = KimHandler(endpoint, mapper_class=MyMapper)
    assert handler.mapper == MyMapper


def test_kim_handler_sets_opts():

    endpoint = CharactersEndpoint()
    handler = KimHandler(
        endpoint,
        mapper_class=MyMapper,
        mapper_kwargs={'foo': 'bar'},
        role='test',
        many=True,
        raw=True)
    assert handler.mapper_class == MyMapper
    assert handler.mapper_kwargs == {'foo': 'bar'}
    assert handler.role == 'test'
    assert handler.many is True
    assert handler.raw is True


def test_kim_handler_default_opts():

    endpoint = CharactersEndpoint()
    handler = KimHandler(endpoint)
    assert handler.mapper_class is None
    assert handler.mapper_kwargs == {}
    assert handler.role == '__default__'
    assert handler.many is False
    assert handler.raw is False


def test_kim_response_handler_with_many():

    data = [MyObject(id=1, name='test 1'), MyObject(id=2, name='test 2')]
    endpoint = CharactersEndpoint()
    handler = KimResponseHandler(endpoint, mapper_class=MyMapper, many=True)

    resp = handler.handle(data)
    assert resp == [{'id': 1, 'name': 'test 1'}, {'id': 2, 'name': 'test 2'}]


def test_kim_response_handler_with_many_and_role():

    data = [MyObject(id=1, name='test 1'), MyObject(id=2, name='test 2')]
    endpoint = CharactersEndpoint()
    handler = KimResponseHandler(
        endpoint, mapper_class=MyMapper, many=True, role='name_only')

    resp = handler.handle(data)
    assert resp == [{'name': 'test 1'}, {'name': 'test 2'}]


def test_kim_response_handler():

    data = MyObject(id=1, name='test 1')
    endpoint = CharactersEndpoint()
    handler = KimResponseHandler(endpoint, mapper_class=MyMapper, many=False)

    resp = handler.handle(data)
    assert resp == {'id': 1, 'name': 'test 1'}


def test_kim_response_handler_role():

    data = MyObject(id=1, name='test 1')
    endpoint = CharactersEndpoint()
    handler = KimResponseHandler(endpoint, mapper_class=MyMapper, role='name_only')

    resp = handler.handle(data)
    assert resp == {'name': 'test 1'}


def test_kim_response_handler_mapper_kwargs():

    mock_mapper = MagicMock(spec=MyMapper)
    data = MyObject(id=1, name='test 1')
    endpoint = CharactersEndpoint()
    handler = KimResponseHandler(
        endpoint, mapper_class=mock_mapper, mapper_kwargs={'test': 1})

    handler.handle(data)
    assert mock_mapper.call_count == 1
    call_args, call_kwargs = mock_mapper.call_args
    assert call_kwargs == {'obj': data, 'raw': False, 'test': 1}


def test_kim_request_handler():

    data = {'name': 'test 1', 'id': 1}
    endpoint = CharactersEndpoint()
    handler = KimRequestHandler(endpoint, mapper_class=MyMapper)

    resp = handler.handle(data)
    assert resp == MyObject(id=1, name='test 1')


def test_kim_request_handler_with_many():

    data = [{'name': 'test 1', 'id': 1}, {'name': 'test 2', 'id': 2}]
    endpoint = CharactersEndpoint()
    handler = KimRequestHandler(endpoint, mapper_class=MyMapper, many=True)

    resp = handler.handle(data)
    assert resp == [MyObject(id=1, name='test 1'), MyObject(id=2, name='test 2')]


def test_kim_request_handler_with_errors():

    data = [{'id': 1}, {'name': 'test 2'}]
    endpoint = CharactersEndpoint()
    handler = KimRequestHandler(endpoint, mapper_class=MyMapper, many=True)

    with pytest.raises(UnprocessableEntity):

        handler.handle(data)


def test_kim_request_handler_with_errors_resp():

    data = [{'id': 1}, {'name': 'test 2'}]
    endpoint = CharactersEndpoint()
    handler = KimRequestHandler(endpoint, mapper_class=MyMapper, many=True)

    try:
        handler.handle(data)
        assert False, 'Did not raise UnprocessableEntity'
    except UnprocessableEntity as resp:
        assert resp.response.data == \
            b'{"message": "Invalid or incomplete data provided.", "errors": {"name": "This is a required field"}}'


def test_kim_request_handler_with_custom_error_status():

    data = [{'id': 1}, {'name': 'test 2'}]
    endpoint = CharactersEndpoint()
    handler = KimRequestHandler(endpoint, mapper_class=MyMapper, many=True)

    try:
        handler.handle(data, error_status=400)
        assert False, 'Did not raise UnprocessableEntity'
    except BadRequest as resp:
        assert resp.response.data == \
            b'{"message": "Invalid or incomplete data provided.", "errors": {"name": "This is a required field"}}'


def test_kim_endpoint_is_marshal_request_false(app):

    with app.test_request_context('/test', method='GET'):
        endpoint = KimEndpoint()
        assert endpoint._is_marshal_request() == False


def test_kim_endpoint_is_marshal_request_true(app):

    def _test(method):
        with app.test_request_context('/test', method=method):
            endpoint = KimEndpoint()
            assert endpoint._is_marshal_request() == True

    [_test(method) for method in ['POST', 'PUT', 'PATCH']]


def test_kim_endpoint_get_response_handler_params(app):

    class MyEndpoint(KimEndpoint):
        mapper_class = MyMapper
        many = True
        serialize_role = 'test'

    with app.test_request_context('/test'):
        endpoint = MyEndpoint()
        params = endpoint.get_response_handler_params()
        exp = {
            'mapper_class': MyMapper,
            'many': True,
            'role': 'test'
        }
        assert params == exp


def test_kim_endpoint_get_request_handler_params(app):

    class MyEndpoint(KimEndpoint):
        mapper_class = MyMapper
        many = True
        marshal_role = 'test'

    with app.test_request_context('/test', method="POST"):
        endpoint = MyEndpoint()
        params = endpoint.get_request_handler_params()
        exp = {
            'mapper_class': MyMapper,
            'many': False,
            'role': 'test',
            'obj': None,
            'partial': False,
        }
        assert params == exp


def test_kim_endpoint_get_request_handler_params_update_existing(app):

    class MyEndpoint(KimEndpoint, PutObjectMixin):
        mapper_class = MyMapper
        many = True
        marshal_role = 'test'

        def get_object(self):

            return {'foo': 'bar'}

    with app.test_request_context('/test', method="PUT"):
        endpoint = MyEndpoint()
        params = endpoint.get_request_handler_params()
        exp = {
            'mapper_class': MyMapper,
            'many': False,
            'role': 'test',
            'obj': {'foo': 'bar'},
            'partial': False,
        }
        assert params == exp


def test_kim_endpoint_get_request_handler_partial_update(app):

    class MyEndpoint(KimEndpoint, PatchObjectMixin):
        mapper_class = MyMapper
        many = True
        marshal_role = 'test'

        def get_object(self):

            return {'foo': 'bar'}

    with app.test_request_context('/test', method="PATCH"):
        endpoint = MyEndpoint()
        params = endpoint.get_request_handler_params()
        exp = {
            'mapper_class': MyMapper,
            'many': False,
            'role': 'test',
            'obj': {'foo': 'bar'},
            'partial': True,
        }
        assert params == exp


def test_kim_endpoint_get_response_handler_params_sets_many_from_request_params(app):

    class MyEndpoint(KimEndpoint):
        mapper_class = MyMapper
        many = False
        marshal_role = 'test'

        def get_request_handler_params(self, **params):

            params = super(MyEndpoint, self).get_request_handler_params(**params)
            params['many'] = True

            return params

    with app.test_request_context('/test', method="POST"):
        endpoint = MyEndpoint()
        params = endpoint.get_response_handler_params()
        exp = {
            'mapper_class': MyMapper,
            'many': True,
            'role': '__default__'
        }
        assert params == exp
