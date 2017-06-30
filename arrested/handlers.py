import json

from flask import request
from werkzeug.exceptions import BadRequest


__all__ = [
    'Handler', 'ResponseHandler', 'RequestHandler',
    'JSONRequestMixin', 'JSONResponseMixin'
]


class Handler(object):

    def __init__(self, endpoint, payload_key='payload', **params):

        self.endpoint = endpoint
        self.params = params
        self.data = None
        self._errors = None
        self.payload_key = payload_key

    def handle(self, data, **kwargs):
        """Invoke the handler to process the provided data.  Concrete classes
        should override this method to provide specific capabilties for the
        choosen method of marshaling and serializing data.

        :param data: The data to be processed by the Handler.
        :returns: The data processed by the Handler
        :rtype: mixed

        Here's an example of a RequestHandler integrating with the Kim library.

        .. code-block:: python

            def handle(self, data):
                try:
                    if self.many:
                        return self.mapper.many(raw=self.raw,
                                                **self.mapper_kwargs) \
                            .marshal(data, role=self.role)
                    else:
                        return self.mapper(data=data, raw=self.raw,
                                           **self.mapper_kwargs) \
                            .marshal(role=self.role)
                except MappingInvalid as e:
                    self.errors = e.errors

        .. seealso:
            :meth:`Handler.process`
        """
        return data

    def process(self, data=None, **kwargs):
        """Process the provided data and invoke :meth:`Handler.handle` method for this
        Handler class.

        :params data: The data being processed.
        :returns: self
        :rtype: :class:`Handler`

        .. code-block:: python

            def post(self, *args, **kwargs):
                self.request = self.get_request_handler()
                self.request.process(self.get_data())
                return self.get_create_response()

        .. seealso:
            :meth:`Handler.process`
        """
        self.data = self.handle(data, **kwargs)
        return self


class JSONResponseMixin(object):
    """Provides handling for serializing the response data as a JSON string.
    """

    def get_response_data(self):
        """serialzie the response data and payload_key as a JSON string.

        :returns: JSON serialized string
        :rtype: bytes
        """

        return json.dumps({self.payload_key: self.data})


class JSONRequestMixin(object):
    """Provides handling for fetching JSON data from the FLask request object.
    """

    def get_request_data(self):
        """Pull JSON from the Flask request object.

        :returns: Deserialized JSON data.
        :rtype: mixed
        :raises: :class:`flask.exceptions.JSONBadRequest`
        """

        try:
            return request.json or {}
        except BadRequest:
            return self.endpoint.return_error(
                400,
                payload={'message': 'Invalid JSON data provided'}
            )


class RequestHandler(Handler, JSONRequestMixin):
    """Basic default RequestHandler that expects the will pull JSON from the Flask request
    object and return it.
    """

    def process(self, data=None):
        """Fetch incoming data from the Flask request object when no data is supplied
        to the process method.  By default, the RequestHandler expects the
        incoming data to be sent as JSON.
        """

        return super(RequestHandler, self).process(data=data or self.get_request_data())


class ResponseHandler(Handler, JSONResponseMixin):
    """Basic default ResponseHanlder that expects the data passed to it to be JSON
    serializable without any modifications.
    """
    pass
