from flask import request

from marshmallow import ValidationError
from ..handlers import Handler, RequestHandler, ResponseHandler
from ..endpoint import Endpoint


class MarshmallowHandler(Handler):

    def __init__(self, endpoint, *args, **params):
        super(MarshmallowHandler, self).__init__(endpoint, *args, **params)

        self.schema_class = params.pop('schema_class', None)
        self.schema_kwargs = params.pop('schema_kwargs', {})
        self.only = params.pop('only', None)
        self.many = params.pop('many', False)

    @property
    def schema(self):
        """Proxy to the provided schema_class property.

        :raises: Exception when required schema_class param is not provided
        :returns: Marshmallow Schema class
        """
        if self.schema_class is None:
            raise Exception('MarshmallowHandler requires a schema_class')

        return self.schema_class


class MarshmallowResponseHandler(MarshmallowHandler, ResponseHandler):

    def handle(self, data, **kwargs):
        """Run serialization for the specified schema_class

        Supports serializing single objects and collections of objects.

        :param data: Objects to be serialized.
        :returns: Serialized data according to Schema configuration
        """

        return self.schema(
            many=self.many,
            only=self.only,
            **self.schema_kwargs
        ).dump(
            data
        ).data


class MarshmallowRequestHandler(MarshmallowHandler, RequestHandler):

    def handle(self, data, error_status=422, **kwargs):
        """Run marshaling for the specified schema_class.

        Supports marshaling single and collection of objects.

        :param data: Data to be marshaled.
        :param error_status: HTTP Status code used when generating an error response
        :returns: Marshaled object according to Schema configuration
        :raises: :class:`werkzeug.exceptions.UnprocessableEntity`
        """

        schema = self.schema(
            many=self.many,
            only=self.only,
            **self.schema_kwargs
        )

        errors = None
        resp = None

        # Marshamallow will only raise ValidationError if the Schema is in "strict" mode.
        # otherwise the resp.errors dict will be populated instead.
        try:
            resp = schema.load(data)
        except ValidationError as err:
            errors = err.messages

        if errors is not None:
            self.handle_error(error_status, errors)
        elif resp is not None and resp.errors:
            self.handle_error(error_status, resp.errors)
        else:
            return resp.data


class MarshmallowEndpoint(Endpoint):

    many = False
    schema_class = None
    only = None
    response_handler = MarshmallowResponseHandler
    request_handler = MarshmallowRequestHandler

    def is_partial(self):
        """Return a boolean indicating if this marshal request is providing partial data
        """
        return request.method == 'PATCH'

    def response_has_many(self):
        """Return a boolean indicating if the request is expecting many objects to be
        marshalled or serialized.

        After a successfull attempt to marshal an object, a response
        is generated using the RepsonseHandler.  Rather than taking the class level
        setting for many by default, pull it from the request handler params config to
        ensure Marshaling and Serializing are run the same way.

        It's typical that the index endpoint of a resource returns a collection of objects
        when making a GET request and create a single object for a POST
        Eg:
            GET /users
            Status 200
            [{...}, {...}]

            POST /users
            Status 201
            {...}

        You can of course support requirements like bulk create for a POST
        to an endpoint by overriding this method and returning True for both GET and POST
        requests.
        """
        if request.method in ['POST', 'PATCH', 'PUT']:
            req_params = self.get_request_handler_params()
            return req_params.get('many', self.many)
        else:
            return self.many

    def get_response_handler_params(self, **params):
        """Return a config object that will be used to configure
        the MarshmallowResponseHandler.

        :returns: a dictionary of config options
        :rtype: dict
        """
        params = super(MarshmallowEndpoint, self).get_response_handler_params(**params)
        params['schema_class'] = self.schema_class
        params['only'] = self.only
        params['many'] = self.response_has_many()

        return params

    def get_request_handler_params(self, **params):
        """Return a config object that will be used to configure the
        MarshamallowRequestHandler

        :returns: a dictionary of config options
        :rtype: dict
        """

        params = super(MarshmallowEndpoint, self).get_request_handler_params(**params)
        params['schema_class'] = self.schema_class
        params['only'] = self.only
        params['many'] = False # By default POST,PUT and PATCH requests create one obj
        params['partial'] = self.is_partial()

        return params
