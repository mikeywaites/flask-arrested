import pytest

from mock import MagicMock
from marshmallow import Schema, fields, post_load
from tests.endpoints import CharactersEndpoint
from werkzeug.exceptions import BadRequest, UnprocessableEntity

from arrested import PutObjectMixin, PatchObjectMixin
from arrested.contrib.marshmallow_arrested import (
    MarshmallowEndpoint,
    MarshmallowHandler,
    MarshmallowResponseHandler,
    MarshmallowRequestHandler
)


class MyObject(object):

    def __init__(self, id=None, name=''):

        self.id = id
        self.name = name

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False



class MySchema(Schema):

    id = fields.Integer()
    name = fields.Str(required=True)

    @post_load
    def make_obj(self, data):
        return MyObject(**data)


def test_schema_property_required_schema_class():

    endpoint = CharactersEndpoint()
    handler = MarshmallowHandler(endpoint, schema_class=None)

    with pytest.raises(Exception):

        handler.schema


def test_get_schema():

    endpoint = CharactersEndpoint()
    handler = MarshmallowHandler(endpoint, schema_class=MySchema)

    handler.schema == MySchema


def test_marshmallow_handler_sets_opts():

    endpoint = CharactersEndpoint()
    handler = MarshmallowHandler(
        endpoint,
        schema_class=MySchema,
        schema_kwargs={'strict': True},
        only=('name', ),
        many=True
    )

    assert handler.schema_class == MySchema
    assert handler.schema_kwargs == {'strict': True}
    assert handler.only == ('name', )
    assert handler.many is True


def test_marshmallow_handler_default_opts():

    endpoint = CharactersEndpoint()
    handler = MarshmallowHandler(
        endpoint
    )

    assert handler.schema_class is None
    assert handler.schema_kwargs == {}
    assert handler.only is None
    assert handler.many is False


def test_marshamallow_response_handler_with_many():

    data = [MyObject(id=1, name='test 1'), MyObject(id=2, name='test 2')]
    endpoint = CharactersEndpoint()
    handler = MarshmallowResponseHandler(endpoint, schema_class=MySchema, many=True)

    resp = handler.handle(data)

    assert resp == [{'id': 1, 'name': 'test 1'}, {'id': 2, 'name': 'test 2'}]


def test_marshamallow_response_handler_with_many_and_only():

    data = [MyObject(id=1, name='test 1'), MyObject(id=2, name='test 2')]
    endpoint = CharactersEndpoint()
    handler = MarshmallowResponseHandler(
        endpoint,
        schema_class=MySchema,
        only=('name', ),
        many=True
    )

    resp = handler.handle(data)

    assert resp == [{'name': 'test 1'}, {'name': 'test 2'}]


def test_marshmallow_response_handler_mapper_kwargs():

    mock_schema = MagicMock(spec=MySchema)
    data = MyObject(id=1, name='test 1')
    endpoint = CharactersEndpoint()
    handler = MarshmallowResponseHandler(
        endpoint,
        schema_class=mock_schema,
        only=('name', ),
        many=True,
        schema_kwargs={'strict': True}
    )

    handler.handle(data)

    mock_schema.assert_called_once_with(
        many=True,
        only=('name', ),
        strict=True
    )


def test_marshmallow_request_handler():

    data = {'name': 'test 1', 'id': 1}
    endpoint = CharactersEndpoint()
    handler = MarshmallowRequestHandler(endpoint, schema_class=MySchema)

    resp = handler.handle(data)

    assert resp == MyObject(id=1, name='test 1')


def test_marshmallow_request_handler_with_many():

    data = [{'name': 'test 1', 'id': 1}, {'name': 'test 2', 'id': 2}]
    endpoint = CharactersEndpoint()
    handler = MarshmallowRequestHandler(endpoint, schema_class=MySchema, many=True)

    resp = handler.handle(data)

    assert resp == [MyObject(id=1, name='test 1'), MyObject(id=2, name='test 2')]


def test_marshmallow_request_handler_with_errors():

    data = [{'id': 1}, {'name': 'test 2'}]
    endpoint = CharactersEndpoint()
    handler = MarshmallowRequestHandler(endpoint, schema_class=MySchema, many=True)

    with pytest.raises(UnprocessableEntity):

        handler.handle(data)


def test_marshmallow_request_handler_with_errors_strict_mode():

    data = [{'id': 1}, {'name': 'test 2'}]
    endpoint = CharactersEndpoint()
    handler = MarshmallowRequestHandler(
        endpoint, schema_class=MySchema, schema_kwargs={'strict': True}, many=True)

    with pytest.raises(UnprocessableEntity):

        handler.handle(data)


def test_marshmallow_request_handler_error_resp():

    data = [{'id': 1}, {'name': 'test 2'}]
    endpoint = CharactersEndpoint()
    handler = MarshmallowRequestHandler(endpoint, schema_class=MySchema, many=True)

    try:
        handler.handle(data)
        assert False, 'Did not raise UnprocessableEntity'
    except UnprocessableEntity as resp:
        assert resp.response.data == \
            b'{"message": "Invalid or incomplete data provided.", "errors": {"0": {"name": ["Missing data for required field."]}}}'


def test_marshmallow_request_handler_custom_error_status():

    data = [{'id': 1}, {'name': 'test 2'}]
    endpoint = CharactersEndpoint()
    handler = MarshmallowRequestHandler(endpoint, schema_class=MySchema, many=True)

    try:
        handler.handle(data, error_status=400)
        assert False, 'Did not raise UnprocessableEntity'
    except BadRequest as resp:
        assert resp.response.status_code == 400


def test_marshmallow_endpoint_get_request_handler_params(app):

    class MyEndpoint(MarshmallowEndpoint, PatchObjectMixin):
        schema_class = MySchema
        many = True

        def get_object(self):

            return {'foo': 'bar'}

    with app.test_request_context('/test', method="POST"):
        endpoint = MyEndpoint()
        params = endpoint.get_request_handler_params()
        exp = {
            'schema_class': MySchema,
            'many': False,
            'only': None,
            'partial': False,
        }
        assert params == exp


def test_marshmallow_endpoint_get_request_handler_partial_update(app):

    class MyEndpoint(MarshmallowEndpoint, PatchObjectMixin):
        schema_class = MySchema
        many = True

        def get_object(self):

            return {'foo': 'bar'}

    with app.test_request_context('/test', method="PATCH"):
        endpoint = MyEndpoint()
        params = endpoint.get_request_handler_params()
        exp = {
            'schema_class': MySchema,
            'many': False,
            'only': None,
            'partial': True,
        }
        assert params == exp


def test_marshmallow_endpoint_is_partial(app):

    class MyEndpoint(MarshmallowEndpoint, PatchObjectMixin):
        schema_class = MySchema
        many = True

        def get_object(self):

            return {'foo': 'bar'}

    with app.test_request_context('/test', method="PATCH"):
        endpoint = MyEndpoint()
        assert endpoint.is_partial() == True


def test_marshmallow_endpoint_response_has_many_get(app):

    class MyEndpoint(MarshmallowEndpoint, PatchObjectMixin):
        schema_class = MySchema
        many = True

        def get_object(self):

            return {'foo': 'bar'}

    with app.test_request_context('/test', method="GET"):
        endpoint = MyEndpoint()
        assert endpoint.response_has_many() == True


def test_marshmallow_endpoint_response_has_many_many_false_in_request_params(app):
    """Assert that the value of many, when making a POST,PUT,PATCH request returns false
    well the value of params['many'] in request handler params is False
    """

    class MyEndpoint(MarshmallowEndpoint, PatchObjectMixin):
        schema_class = MySchema
        many = True

        def get_object(self):

            return {'foo': 'bar'}

    with app.test_request_context('/test', method="POST"):
        endpoint = MyEndpoint()
        assert endpoint.response_has_many() == False


def test_marshmallow_endpoint_response_has_many_many_true_in_request_params(app):
    """Assert that the value of many, when making a POST,PUT,PATCH request returns false
    well the value of params['many'] in request handler params is True
    """

    class MyEndpoint(MarshmallowEndpoint, PatchObjectMixin):
        schema_class = MySchema
        many = True

        def get_object(self):

            return {'foo': 'bar'}

        def get_request_handler_params(self, **params):

            params = super(MyEndpoint, self).get_request_handler_params(**params)
            params['many'] = True

            return params

    with app.test_request_context('/test', method="POST"):
        endpoint = MyEndpoint()
        assert endpoint.response_has_many() == True


def test_marshal_endpoint_get_response_handler_params(app):

    class MyEndpoint(MarshmallowEndpoint):
        schema_class = MySchema
        many = True

    with app.test_request_context('/test'):
        endpoint = MyEndpoint()
        params = endpoint.get_response_handler_params()
        exp = {
            'schema_class': MySchema,
            'many': True,
            'only': None
        }
        assert params == exp
