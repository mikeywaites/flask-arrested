import json
from werkzeug.wrappers import Response

from itertools import chain

from flask import Response, abort, request, current_app
from flask.views import MethodView

from .handlers import ResponseHandler, RequestHandler


class Endpoint(MethodView):
    """The Endpoint class represents the HTTP methods that can be called against an
    Endpoint inside of a particular resource.
    """

    #: list containing the permitted HTTP methods this endpoint accepts
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

    #: The name used to register this endpoint with Flask's url_map
    name = None

    #: A :class:`.ResponseHandler` class
    response_handler = ResponseHandler

    #: A :class:`.RequestHandler` class
    request_handler = RequestHandler

    #: The URL this endpoint is mapped against. This will build on top of any url_prefix
    #: defined at the API and Resource level
    url = ''

    #: A list of functions called before any specific request handler methods are called
    before_all_hooks = []

    #: A list of functions called before GET requests are dispatched
    before_get_hooks = []

    #: A list of functions called after GET requests are dispatched
    after_get_hooks = []

    #: A list of functions called before POST requests are dispatched
    before_post_hooks = []

    #: A list of functions called after POST requests are dispatched
    after_post_hooks = []

    #: A list of functions called before PUT requests are dispatched
    before_put_hooks = []

    #: A list of functions called after PUT requests are dispatched
    after_put_hooks = []

    #: A list of functions called before PATCH requests are dispatched
    before_patch_hooks = []

    #: A list of functions called after PATCH requests are dispatched
    after_patch_hooks = []

    #: A list of functions called before DELETE requests are dispatched
    before_delete_hooks = []

    #: A list of functions called after DELETE requests are dispatched
    after_delete_hooks = []

    #: A list of functions called after all requests are dispatched
    after_all_hooks = []

    def dispatch_request(self, *args, **kwargs):
        """Dispatch the incoming HTTP request to the appropriate handler.
        """
        self.args = args
        self.kwargs = kwargs
        meth = request.method.lower()

        if request.method not in self.methods:
            self.return_error(405)

        resource = current_app.blueprints.get(request.blueprint, None)
        if resource:
            for hook in chain(resource.api.before_all_hooks, resource.before_all_hooks):
                hook(self)

        before_hooks = getattr(self, 'before_{method}_hooks'.format(method=meth))
        for hook in before_hooks:
            hook(self)

        resp = super(Endpoint, self).dispatch_request(*args, **kwargs)
        resp = self.make_response(resp)

        after_hooks = getattr(self, 'after_{method}_hooks'.format(method=meth))
        for hook in after_hooks:
            resp = hook(self, resp)

        if resource:
            for hook in chain(resource.after_all_hooks, resource.api.after_all_hooks):
                resp = hook(self, resp)

        return resp

    @classmethod
    def get_name(cls):
        """Returns the user provided name or the lower() class name for use when
        registering the Endpoint with a :class:`Resource`.

        :returns: registration name for this Endpoint.
        :rtype: string
        """
        return cls.name or cls.__name__.lower()

    def make_response(self, rv, status=200, headers=None, mime='application/json'):
        """Create a response object using the :class:`flask.Response` class.

        :param rv: Response value.  If the value is not an instance
            of :class:`werkzeug.wrappers.Response` it will be converted
            into a Response object.
        :param status: specify the HTTP status code for this response.
        :param mime: Specify the mimetype for this request.
        :param headers: Specify dict of headers for the response.

        """
        if not isinstance(rv, Response):
            resp = Response(
                response=rv,
                headers=headers,
                mimetype=mime,
                status=status
            )
        else:
            resp = rv

        return resp

    def get_response_handler_params(self, **params):
        """Return a dictionary of options that are passed to the
        specified :class:`ResponseHandler`.

        :returns: Dictionary of :class:`ResponseHandler` config options.
        :rtype: dict
        """
        return params

    def get_response_handler(self):
        """Return the Endpoints defined :attr:`Endpoint.response_handler`.

        :returns: A instance of the Endpoint specified :class:`ResonseHandler`.
        :rtype: :class:`ResponseHandler`
        """
        assert self.response_handler is not None, \
            'Please define a response_handler ' \
            ' for Endpoint: %s' % self.__class__.__name__

        return self.response_handler(self, **self.get_response_handler_params())

    def get_request_handler_params(self, **params):
        """Return a dictionary of options that are passed to the
        specified :class:`RequestHandler`.

        :returns: Dictionary of :class:`RequestHandler` config options.
        :rtype: dict
        """
        return params

    def get_request_handler(self):
        """Return the Endpoints defined :attr:`Endpoint.request_handler`.

        :returns: A instance of the Endpoint specified :class:`RequestHandler`.
        :rtype: :class:`RequestHandler`
        """
        assert self.request_handler is not None, \
            'Please define a request_handler ' \
            ' for Endpoint: %s' % self.__class__.__name__

        return self.request_handler(self, **self.get_request_handler_params())

    def return_error(self, status, payload=None, as_json=True,
                     headers=None, content_type='application/json'):
        """Error handler called by request handlers when an error occurs and the request
        should be aborted.

        By default, the error is returned using the application/json content type and
        The payload is serialized to JSON.  If you want to return a different
        content type you can do so using the content_type kwarg.  You can stop the
        payload being serialized as JSON by passing as_json=False

        *A special note about METHOD NOT ALLOWED.*

        When return_error is called with a 405 status no response is created.  Werkzeug's
        exception that handles this response does not allow a response body to be
        provided.

        See the link below for more info.
        http://werkzeug.pocoo.org/docs/0.12/exceptions/#werkzeug.exceptions.MethodNotAllowed

        :param status: HTTP status code for this error
        :param payload: Response body. When as_json=True is passed to this function
            the payload will be serialized as a JSON string.
        :param as_json: Serialize the payload as a JSON string
        :param headers: a dict of headers to return with response
        :param content_type: specify the content type to return with the response

        Usage::

            def handle_post_request(self, *args, **kwargs):

                self.request_handler = self.get_request_handler()
                try:
                    self.request_handler.process(self.get_data())
                except SomeException as e:
                    self.return_error(400, payload=self.request_handler.errors)

                return self.return_create_response()
        """

        if status in [405]:
            abort(status)
        else:

            if as_json:
                payload = json.dumps(payload)

            resp = self.make_response(
                payload, status=status, headers=headers, mime=content_type
            )

            abort(status, response=resp)

    def get(self, *args, **kwargs):
        """Handle Incoming GET requests and dispatch to handle_get_request method.
        """
        return self.handle_get_request()

    def post(self, *args, **kwargs):
        """Handle Incoming POST requests and dispatch to handle_post_request method.
        """
        return self.handle_post_request()

    def put(self, *args, **kwargs):
        """Handle Incoming PUT requests and dispatch to handle_put_request method.
        """
        return self.handle_put_request()

    def patch(self, *args, **kwargs):
        """Handle Incoming PATCH requests and dispatch to handle_patch_request method.
        """
        return self.handle_patch_request()

    def delete(self, *args, **kwargs):
        """Handle Incoming DELETE requests and dispatch to handle_delete_request method.
        """
        return self.handle_delete_request()
