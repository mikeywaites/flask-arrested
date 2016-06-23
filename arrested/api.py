# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import inspect

from flask import request, Response
from flask.views import MethodView


def hook(methods=['GET'], type_='before_request'):
    """register a method to be called before or after a request to a resource
    is processed.

    The difference between this decorator and the built in hooks available from
    Flask is that this before hook will conditionaly run based on the HTTP
    verb and the endpoint being called.

    .. code-block:: python

        class MyResource(Resource):

            @hook(method='GET', type_='before_request')
            def log_request(self):

                log.info('request')

    :param methods: Specify the HTTP verbs that this hook should be run on
    :param type_: specify one of before_request and after_request

    """

    def hook_decorator(func):

        def func_wrapper(*args, **kwargs):
            self = args[0]
            if (request.method.upper() in methods
                    and request.endpoint == '%s.%s'
                    % (self.app.name, self.endpoint_name)):

                return func(*args, **kwargs)
            else:
                return None

        func_wrapper.__apihook__ = type_
        return func_wrapper

    return hook_decorator


class Api(MethodView):
    """TODO(mike) Docs
    """

    endpoint_name = None
    methods = ['GET']

    def make_response(self, json_data, status=200):
        """Create a JSON response object using the :py:class:`flask.Response`
        class.

        :param json_data: Valid JSON string
        :param status: specify the HTTP status code for this response
        """
        resp = Response(
            response=json_data,
            mimetype='application/json',
            status=status)

        return resp

    @classmethod
    def as_view(cls, name=None, api=None):
        """return a func that can be used by Flask routing system and allow
        name to be an optional value.  When `name` is not supplied the
        `Resource.endpoint` will be used.

        :param name: specify a name used for routing for this Resource
        """

        endpoint_name = name or cls.endpoint
        assert endpoint_name is not None, \
            '%s endpoint name cannot be None' % cls.__name__

        view = super(Api, cls).as_view(endpoint_name)
        return view

    def _get_hooks(self, type_):
        """Find all the hooks registerd on this Resource for a given ``type_``.

        :param type_: Specify the type of hooks return
        """
        methods = inspect.getmembers(self, predicate=inspect.ismethod)

        hooks = []
        for name, method in methods:
            if getattr(method, '__apihook__', None) == type_:
                hooks.append(method)

        return hooks

    def get_before_hooks(self):
        """return a list of registerd before_request hooks for this resource.

        Before request hooks are defined on a per request, per method basis.

        .. code-block:: python

            class MyResource(Resource):

                @hook(method='GET', type_='before_request')
                def log_request(self):

                    log.info('request')

        """
        return self._get_hooks('before_request')

    def get_after_hooks(self):
        """return a list of registerd after_request hooks for this resource.

        After request hooks are defined on a per request, per method basis.
        Unlike before_request hooks, after_request hooks must accept and return
        the request object.

        The hooks are registered as :py:class:`Flask.after_request`
        and therefore follow the same rules.

        .. code-block:: python

            class MyResource(Resource):

                @hook(method='GET', type_='after_hooks')
                def log_request(self, request, *args, **kwargs):

                    log.info('request')

                    return request

        """
        return self._get_hooks('after_request')


class Resource(object):

    request_handler = None
    response_handler = None

    def get_response_handler_params(self, **params):
        """Return a dictionary of params to pass to :py:class:`ResponseHandler`

        :param params: A dictionary containing config options
        """

        return params

    def get_request_handler_params(self, **params):
        """Return a dictionary of params to pass to :py:class:`RequestHandler`

        :param params: A dictionary containing config options
        """

        return params

    def get_response_handler(self):
        """Return a response handler instance for this Resource.
        """

        assert self.response_handler is not None, \
            'Please define a response_handler ' \
            ' for Resource: %s' % self.__class__.__name__

        return self.response_handler(**self.get_response_handler_params())

    def get_request_handler(self):
        """Return a request handler instance for this Resource.
        """
        assert self.request_handler is not None, \
            'Please define a request_handler ' \
            ' for Resource: %s' % self.__class__.__name__

        return self.request_handler(**self.get_request_handler_params())


class BaseListableResource(Resource):
    """BaseListableResource provides abilities for handling `GET` requests.

    BaseListableResource represents a list of items described by a RESTFul
    url such as htttps://api.example.com/v1/users.

    .. code-block:: python

        from arrested import Api, BaseListableResource

        class UsersApi(Api, BaseListableResource):

            url = '/users'
            endpoint_name='users.index'
            response_handler = KimResponseHandler

            def get_objects(self):

                return get_users()

    Users must provide a :py:class:`ResponseHandler` when
    accepting `GET` requests.

    .. seealso:
        :meth:`get`

    """

    def get_list_response(self, status=200):
        """Called by :meth:`get` to process a collection of objects and return
        a valid json response.

        This method can be overriden to provide your own falvour or response
        generation where required but typically this is done by implementing
        custom :py:class:`ResponseHandler`.

        :param status: The HTTP status code returned with the response

        .. seealso:
            :meth:`make_response`
        """

        return (self.make_response(self.response.to_json(), status=status))

    def get(self, *args, **kwargs):
        """Handles a GET request for a resource and returns an
        array of results.

        A :py:class:`.handlers.ResponseHandler` is required to accept GET
        requests.

        Users must also define the :meth:`get_objects` which returns an
        iterable containing objects that will be serialized by
        the `reponse_handler`.  This is typically done using a
        :py:class:`ListMixin` provided or by a custom mixin.

        .. code-block:: python

            from arrested import Api, BaseListableResource
            from arrested.mixins import ListMixin

            class UsersApi(Api, BaseListableResource):

                url = '/users'
                endpoint_name='users.index'
                response_handler = KimResponseHandler

                def get_objects(self):

                    return get_users()

        This method will itself call the :meth:`get_list_response` method where
        the response handler will actually process the objects returned from
        :meth:`get_objects`

        .. seealso:
            :meth:`get_list_response`
        """
        if not hasattr(self, 'get_objects'):
            raise NotImplementedError('Please implement the get_objects')

        self.response = self.get_response_handler()

        self.objects = self.get_objects()

        # TODO(mike) we need to handle the processing error's raised by
        # ResponsHandler here and call :meth:on_errors
        self.response.process(self.objects)

        return self.get_list_response()


class BaseCreateableResource(Resource):
    """BaseCreateableResource provides abilities for handling `POST` requests.

    .. code-block:: python

        from arrested import IndexApi
        from arrested.mixins import ListMixin

        class UsersApi(Api, BaseCreateableResource):

            url = '/users'
            endpoint_name='users.index'
            request_handler = KimRequestHandler
            methods = ['POST']

            def save_object(self):

                obj = self.request.data
                db.session.add(obj)
                db.session.flush()

    Users must provide a :py:class:`RequestHandler` and
    a :py:class:`ResponseHandler` accepting `POST` requests.

    .. seealso:
        :meth:`post`

    """

    def save_object(self):
        """TODO(mike) Docs
        """
        pass

    def get_create_response(self, status=201):
        """Once an incoming data set has been processed by the RequestHandler,
        we typically want to return the serialized version of our newly created
        object.

        This method will call the :py:class:`ResponseHandler` defined with the
        data processed by the :py:class:`RequestHandler` and the return
        the serialzied version of that object.

        :param status: Specify the HTTP status code for this response

        .. seealso:
            :meth:`make_response`
        """

        self.response = self.get_response_handler()
        self.response.process(self.request.data)

        return (self.make_response(self.response.to_json(), status=status))

    def post(self, *args, **kwargs):
        """Handles an incoming POST request for a resource and returns
        a JSON serialized version of the newly created object.

        A :py:class:`.handlers.RequestHandler` is required to accept POST
        requests.

        Users must also define the :meth:`get_data` which should parse the
        incoming data, typically json and return the object as a valid type
        for the request handler to process.  This is typically done using one
        of the :py:class:`CreateMixin` provided or by a custom mixin.

        .. code-block:: python

            from flask import request as flask_request
            from arrested import Api, BaseCreateableResource
            from arrested.mixins import CreateMixin

            class UsersApi(Api, CreateableResource):

                url = '/users'
                endpoint_name='users.index'
                request_handler = KimRequestHandler

                def get_data(self):

                    return flask_request.json()

        .. seealso:
            :meth:`get_create_response`
        """
        if not hasattr(self, 'get_data'):
            raise NotImplementedError('Please implement the get_data method')

        self.request = self.get_request_handler()

        # TODO(mike) we need to handle the processing error's raised by
        # RequestHanlder here and call :meth:on_errors
        self.request.process(self.get_data())

        self.save_object()

        return self.get_create_response()
