from flask import request
from kim.exception import MappingInvalid

from ..handlers import Handler, RequestHandler, ResponseHandler
from ..endpoint import Endpoint


__all__ = ['KimHandler', 'KimRequestHandler', 'KimResponseHandler', 'KimEndpoint']


class KimHandler(Handler):
    """Base handler providing Request/Response handling for the Kim serialization and
    marshaling framework.
    """

    def __init__(self, endpoint, *args, **params):
        """KimHandler constructor that creates a new instance of a :class:`KimHandler`.

        :param mapper_class: a Kim Mapper class
        :param mapper_kwargs: a dictionary of config options passed to the mapper each
            time it is instantiated.
        :param role: Optionally provide a role to be used by kim when serializing or
            marshaling.
        :param many: Pass the many option to Kim when marshaling or serializing.
        :param raw: Pass the raw option to Kim when marshaling or serializing.
        :returns: None
        """
        super(KimHandler, self).__init__(endpoint, *args, **params)

        self.mapper_class = params.pop('mapper_class', None)
        self.mapper_kwargs = params.pop('mapper_kwargs', {})
        self.role = params.pop('role', '__default__')
        self.many = params.pop('many', False)
        self.raw = params.pop('raw', False)
        self.obj = params.pop('obj', None)
        self.partial = params.pop('partial', False)

    @property
    def mapper(self):
        """Proxy to the provided mapper_class property.

        :raises: Exception when required mapper_class param is not provided
        :returns: Kim Mapper class
        """
        if self.mapper_class is None:
            raise Exception('KimHandler requires a Kim mapper_class')

        return self.mapper_class


class KimResponseHandler(KimHandler, ResponseHandler):
    """ResponseHandler for the Kim serialization and marshaling framework.

    .. code-block:: python

        from arrested.contrib.kim import KimResponseHandler

        class PlanetsEndpoint(Endpoint, DBListMixin):

            name = 'list'
            response_handler = KimResponseHandler

            def get_response_handler_params(self, **params):

                params = super(PlanetsEndpoint, self).get_response_handler_params(**params)
                params['mapper_class'] = PlanetMapper
                params['many'] = True

                return params

            def get_query(self):

                return db.session.query(Planet).order_by(
                    Planet.created_at.desc()
                )
    """

    def handle(self, data, **kwargs):
        """Run serialization for the specified mapper_class.

        Supports both .serialize and .many().serialize Kim interfaces.

        :param data: Objects to be serialized.
        :returns: Serialized data according to mapper configuration
        """
        if self.many:
            return self.mapper.many(raw=self.raw, **self.mapper_kwargs).serialize(
                data, role=self.role
            )
        else:
            return self.mapper(obj=data, raw=self.raw, **self.mapper_kwargs).serialize(
                role=self.role
            )


class KimRequestHandler(KimHandler, RequestHandler):
    """RequestHanlder for the Kim marshaling and serialization framework.

    .. code-block:: python

        from arrested.contrib.kim import KimRequestHandler

        class PlanetsEndpoint(Endpoint, DBListMixin):

            name = 'list'
            request_handler = KimRequestHandler

            def get_request_handler_params(self, **params):

                params = super(PlanetsEndpoint, self).get_response_handler_params(**params)
                params['mapper_class'] = PlanetMapper
                params['many'] = False

                return params

            def get_query(self):

                return db.session.query(Planet).order_by(
                    Planet.created_at.desc()
                )
    """

    def handle(self, data, error_status=422, **kwargs):
        """Run marshalling for the specified mapper_class.

        * TODO(mike) Allows users to control the error reponse generated.

        Supports both .marshal and .many().marshal Kim interfaces.  Handles errors raised
        during marshalling and automatically returns a HTTP error response.

        :param data: Data to be marshaled.
        :returns: Marshaled object according to mapper configuration
        :raises: :class:`werkzeug.exceptions.UnprocessableEntity`
        """
        try:
            if self.many:
                return self.mapper.many(raw=self.raw, **self.mapper_kwargs).marshal(
                    data, role=self.role
                )
            else:
                return self.mapper(
                    data=data,
                    obj=self.obj,
                    partial=self.partial,
                    **self.mapper_kwargs
                ).marshal(role=self.role)
        except MappingInvalid as e:
            payload = {
                "message": "Invalid or incomplete data provided.",
                "errors": e.errors
            }
            self.endpoint.return_error(error_status, payload=payload)


class KimEndpoint(Endpoint):
    """This Endpoint provides all the functionality of the normal Arrested Endpoint class
    plus a few helpers for working with Kim to avoid duplicate code.
    """

    many = False
    mapper_class = None
    serialize_role = '__default__'
    marshal_role = '__default__'
    response_handler = KimResponseHandler
    request_handler = KimRequestHandler

    def _is_marshal_request(self):
        """Return a boolean indicating wether the request is a POST PATCH or PUT request
        """
        return request.method in ['POST', 'PATCH', 'PUT']

    def is_partial(self):
        """Return a boolean indicating if this marshal request is providing partial data
        """
        return request.method == 'PATCH'

    def get_response_handler_params(self, **params):
        """Return a config object that will be used to configure the KimResponseHandler

        :returns: a dictionary of config options
        :rtype: dict
        """

        params = super(KimEndpoint, self).get_response_handler_params(**params)
        params['mapper_class'] = self.mapper_class
        params['role'] = self.serialize_role

        # After a successfull attempt to marshal an object has been made, a response
        # is generated using the RepsonseHandler.  Rather than taking the class level
        # setting for many by default, pull it from the request handler params config to
        # ensure Marshaling and Serializing are run the same way.
        if self._is_marshal_request():
            req_params = self.get_request_handler_params()
            params['many'] = req_params.get('many', self.many)
        else:
            params['many'] = self.many

        return params

    def get_request_handler_params(self, **params):
        """Return a config object that will be used to configure the KimRequestHandler

        :returns: a dictionary of config options
        :rtype: dict
        """

        params = super(KimEndpoint, self).get_request_handler_params(**params)
        params['mapper_class'] = self.mapper_class
        params['role'] = self.marshal_role
        params['many'] = False
        # when handling a PUT or PATCH request, self.obj will be set.. There might be a
        # more robust way to handle this?
        params['obj'] = getattr(self, 'obj', None)
        params['partial'] = self.is_partial()

        return params
