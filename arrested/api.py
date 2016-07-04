# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import inspect
import json

from sqlalchemy.orm.exc import NoResultFound

from flask import request, Response, abort
from flask.views import MethodView

from .contrib.kim import KimRequestHandler, KimResponseHandler
from .contrib.sqa import SqlAlchemyPaginator
from .mixins import ModelMixin


def hook(methods=['GET'], type_='before_request'):
    """register a method to be called before or after a request to a resource
    is processed.

    The difference between this decorator and the built in hooks available from
    Flask is that this before hook will conditionaly run based on the HTTP
    verb and the endpoint being called.

    .. sourcecode:: python

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
    methods = ['GET', 'PUT', 'POST', 'DELETE', 'PATCH']
    response_payload_key = 'payload'

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

    def dispatch_request(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return super(Api, self).dispatch_request(*args, **kwargs)

    def reponse_payload(self, payload, **extra):
        """TODO(mike) Docs
        """

        data = {self.response_payload_key: payload}
        data.update(extra)

        return data

    def make_response(self, data, extra_data=None, headers=None, status=200):
        """Create a JSON response object using the :py:class:`flask.Response`
        class.

        :param data: Response payload to be serialized
        :param status: specify the HTTP status code for this response
        """
        extra_data = extra_data or {}
        resp = Response(
            response=json.dumps(self.reponse_payload(data, **extra_data)),
            mimetype='application/json',
            headers=headers,
            status=status)

        return resp

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

        .. sourcecode:: python

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

        .. sourcecode:: python

            class MyResource(Resource):

                @hook(method='GET', type_='after_hooks')
                def log_request(self, request, *args, **kwargs):

                    log.info('request')

                    return request

        """
        return self._get_hooks('after_request')

    def get_data(self):
        """Handle incoming request and marshal request body into a native
        python object.
        """
        return request.json

    def serialize_errors(self, error_data):
        """Return a serialized version of error_data for error response
        body.

        :param error_data: error data to be serialized
        """
        return {
            'error': True,
            'errors': error_data
        }

    def on_errors(self, error_data, status=400, headers=None, **kwargs):
        """Return a HTTP response with a ``status`` and serialized errors.

        :param status: HTTP status code
        :param errors: a serializable object of errors to return
            as the response body
        """
        resp = self.make_response(self.serialize_errors(error_data),
                                  headers=headers,
                                  status=status)
        session = self.get_session()
        session.rollback()
        abort(resp)


class HttpResource(object):
    """TODO(mike) Docs
    """

    model = None
    marshal_role = '__default__'
    serialize_role = '__default__'
    mapper_class = None
    raw = False
    response_handler = KimResponseHandler
    request_handler = KimRequestHandler
    serialize_create_role = '__default__'

    def get_response_handler_params(self, **params):
        """Return a dictionary of params to pass to :py:class:`ResponseHandler`

        :param params: A dictionary containing config options
        """
        params = self.get_mapper_params(**params)

        return params

    def get_request_handler_params(self, **params):
        """Return a dictionary of params to pass to :py:class:`RequestHandler`

        :param params: A dictionary containing config options
        """
        params = self.get_mapper_params(**params)

        return params

    def get_response_handler(self, **params):
        """Return a response handler instance for this Resource.
        """

        assert self.response_handler is not None, \
            'Please define a response_handler ' \
            ' for Resource: %s' % self.__class__.__name__

        return self.response_handler(**params)

    def get_request_handler(self, **params):
        """Return a request handler instance for this Resource.
        """
        assert self.request_handler is not None, \
            'Please define a request_handler ' \
            ' for Resource: %s' % self.__class__.__name__

        return self.request_handler(**params)

    def get_mapper_params(self, **params):
        """TODO(mike) Docs
        """
        params['mapper_class'] = self.mapper_class
        params['raw'] = self.raw

        return params


class ListableResource(HttpResource, ModelMixin):
    """ListableResource provides abilities for handling `GET` requests.

    ListableResource represents a list of items described by a RESTFul
    url such as htttps://api.example.com/v1/users.

    .. sourcecode:: python

        from arrested import Api, ListableResource

        class UsersApi(Api, ListableResource):

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

    paginator_class = SqlAlchemyPaginator
    paginate = True
    num_per_page = 10
    _paginated = None
    allow_empty = True
    page_kwarg = 'page'
    per_page_param = 'per_page'

    def get_list_response_params(self, **params):

        params = self.get_response_handler_params(**params)
        params['many'] = True
        params['role'] = self.serialize_role

        return params

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

        extra = None
        if self._paginated:
            extra = {
                'meta': {
                    'per_page': self._paginated.per_page,
                    'total_pages': self._paginated.pages,
                    'total_objects': self._paginated.total,
                    'current_page': self._paginated.page,
                    'next_page': self._paginated.next_page,
                    'prev_page': self._paginated.prev_page
                }
            }

        return (self.make_response(
            self.response.data, extra_data=extra, status=status))

    def get_num_per_page(self):
        """ Get the number of items to paginate by, or
        ``None`` for no pagination.
        """
        per_page = request.args.get(self.per_page_param, self.num_per_page)
        try:
            return int(per_page)
        except (ValueError, TypeError):
            return self.num_per_page

    def get_page(self):
        """Return the current page number set at `page_kwarg` in
        :obj:`flask.request` or return 1 for the first page
        :returns: int
        """
        try:
            val = int(request.args.get(self.page_kwarg, 1))
            return val or 1
        except ValueError:
            return 1

    def get_objects(self):
        """Return a list of instances produced from :meth:`get_query` and
        optionally paginate them.

        """
        query = self.get_query()

        page = self.get_page()
        if self.paginate:
            self._paginated = self.paginator_class(
                query,
                page,
                self.get_num_per_page()
            )
            return self._paginated.items
        else:
            return query.all()

    def get(self, *args, **kwargs):
        """Handles a GET request for a resource and returns an
        array of results.

        A :py:class:`.handlers.ResponseHandler` is required to accept GET
        requests.

        Users must also define the :meth:`get_objects` which returns an
        iterable containing objects that will be serialized by
        the `reponse_handler`.  This is typically done using a
        :py:class:`ListMixin` provided or by a custom mixin.

        This method will itself call the :meth:`get_list_response` method where
        the response handler will actually process the objects returned from
        :meth:`get_objects`

        .. seealso:
            :meth:`get_list_response`
        """
        self.response = \
            self.get_response_handler(**self.get_list_response_params())

        self.objects = self.get_objects()

        self.response.process(data=self.objects)

        return self.get_list_response()


class CreateableResource(HttpResource):
    """CreateableResource provides abilities for handling `POST` requests.

    .. sourcecode:: python

        from arrested import Api, CreateableResource

        class UsersApi(Api, CreateableResource):

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

    def get_create_response_params(self, **params):
        """TODO(mike) Docs
        """

        params = self.get_response_handler_params(**params)
        params['role'] = self.serialize_role

        return params

    def get_create_request_params(self, **params):
        """TODO(mike) Docs
        """

        params = self.get_request_handler_params(**params)
        params['role'] = self.marshal_role

        return params

    def save_object(self):
        """TODO(mike) Docs
        """
        db = self.get_session()
        db.add(self.obj)
        db.commit()

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

        self.response = \
            self.get_response_handler(**self.get_create_response_params())
        self.response.process(data=self.obj)

        return (self.make_response(self.response.data, status=status))

    def post(self, *args, **kwargs):
        """Handles an incoming POST request for a resource and returns
        a JSON serialized version of the newly created object.

        A :py:class:`.handlers.RequestHandler` is required to accept POST
        requests.

        Users must also define the :meth:`save_object` which should handle
        the data marshaled by the ``request_handler``.  This is typically
        done using one of the :py:class:`CreateMixin` provided
        or by a custom mixin.

        .. seealso:
            :meth:`get_create_response`
        """
        self.request = \
            self.get_request_handler(**self.get_create_request_params())

        self.obj = self.request.process(data=self.get_data()).data
        if self.request.errors is not None:

            return self.on_errors(self.request.errors, status=400)

        self.save_object()

        return self.get_create_response()


class SingleObjectMixin(ModelMixin):

    model_id_col_name = 'id'
    url_id_param_name = 'obj_id'  # primary key param name for url kwargs

    def get_object_id(self):

        return self.kwargs[self.url_id_param_name]

    def get_object(self):
        """Returns the object looked up by id.

        """
        query = self.get_query()
        obj_id = self.get_object_id()
        try:
            q = query.filter_by(**{self.model_id_col_name: obj_id})
            return q.one()
        except NoResultFound:
            self.on_errors({'not_found': 'Object not found'}, status=404)


class ObjectResource(HttpResource, SingleObjectMixin):
    """ObjectResource provides abilities for handling `GET` requests to
    fetch data for single objects.

    .. sourcecode:: python

        from arrested import Api, ObjectResource

        class UserObjectApi(Api, ObjectResource):

            url = '/users/<string:obj_id>'
            endpoint_name='users.object'
            request_handler = KimRequestHandler
            methods = ['GET']
            id_param_name = 'obj_id'

            def get_object(self):

                return get_user_by_id(self.kwargs[self.id_param_name])

    Users must provide a :py:class:`ResponseHandler` to accept GET requests
    with ObjectResource endpoints.

    .. seealso:
        :meth:`get`

    """

    def get_object_response(self, status=200):
        """Called by :meth:`get` to process a collection of objects and return
        a valid json response.

        This method can be overriden to provide your own falvour or response
        generation where required but typically this is done by implementing
        custom :py:class:`ResponseHandler`.

        :param status: The HTTP status code returned with the response

        .. seealso:
            :meth:`make_response`
        """

        return (self.make_response(self.response.data, status=status))

    def get_object_response_params(self, **params):

        params = self.get_response_handler_params(**params)
        params['role'] = self.serialize_role

        return params

    def get(self, *args, **kwargs):
        """Handles a GET request for a resource and returns a single object.

        A :py:class:`.handlers.ResponseHandler` is required to accept GET
        requests.

        Users must also define the :meth:`get_object` which returns an
        object that will be serialized by the `reponse_handler`.
        This is typically done using a :py:class:`ObjectMixin` provided or
        by a custom mixin.

        This method will itself call the :meth:`get_object_response` method
        where the response handler will actually process the object returned
        from :meth:`get_object`

        .. seealso:
            :meth:`get_object_response`
        """
        self.response = \
            self.get_response_handler(**self.get_object_response_params())

        self.obj = self.get_object()

        self.response.process(data=self.obj)

        return self.get_object_response()


class PatchableResource(HttpResource, SingleObjectMixin):
    """UpdateableResource provides abilities for handling `PUT` requests to
    update data for single objects.

    .. sourcecode:: python

        from arrested import Api, ObjectResource

        class UserObjectApi(Api, ObjectResource):

            url = '/users/<string:obj_id>'
            endpoint_name='users.object'
            request_handler = KimRequestHandler
            methods = ['GET']
            id_param_name = 'obj_id'

            def get_object(self):

                return get_user_by_id(self.kwargs[self.id_param_name])

    Users must provide a :py:class:`ResponseHandler` to accept GET requests
    with ObjectResource endpoints.

    .. seealso:
        :meth:`get`

    """

    def get_mapper_params(self, **params):

        params = super(PatchableResource, self).get_mapper_params(**params)
        params['partial'] = True

        return params

    def get_patch_response(self, status=200):
        """Called by :meth:`put` to process an object and return
        a valid json response.

        This method can be overriden to provide your own flavour of response
        generation where required but typically this is done by implementing
        custom :py:class:`ResponseHandler`.

        :param status: The HTTP status code returned with the response

        .. seealso:
            :meth:`make_response`
        """
        self.response = \
            self.get_response_handler(**self.get_patch_response_params())
        self.response.process(data=self.obj)

        return (self.make_response(self.response.data, status=status))

    def get_patch_request_params(self, **params):

        params = self.get_request_handler_params(**params)
        params['role'] = self.marshal_role

        return params

    def get_patch_response_params(self, **params):

        params = self.get_request_handler_params(**params)
        params['role'] = self.serialize_role

        return params

    def patch_object(self):
        """TODO(mike) Docs
        """
        session = self.get_session()
        session.add(self.obj)
        session.commit()

    def patch(self, *args, **kwargs):
        """Handles a PUT request for a resource updates a single object.

        A :class:`.handlers.ResponseHandler` and
        :class`.handlers.RequesHandler`is required to accept PUT
        requests.

        Users must also define the :meth:`update_object` which returns an
        object that will be serialized by the `reponse_handler`.
        This is typically done using a :py:class:`ObjectMixin` provided or
        by a custom mixin.

        UpdateableResource resources also require `get_object` be
        implemented.  This object will be the object that gets updated
        with the data from the PUT request.

        This Resource would typically be used in conjunction with
        :class:`.ObjectResource` and therefore get_object would
        be implemented .

        This method will itself call the :meth:`get_update_response` method
        where the response handler will actually process the object returned
        from :meth:`get_object`

        .. seealso:
            :meth:`get_update_response`
        """

        self.request = \
            self.get_request_handler(**self.get_patch_request_params())

        self.obj = \
            self.request.process(
                self.get_data(), instance=self.get_object()).data

        if self.request.errors is not None:

            return self.on_errors(self.request.errors, status=400)

        self.patch_object()

        return self.get_patch_response()


class UpdateableResource(HttpResource, SingleObjectMixin):
    """UpdateableResource provides abilities for handling `PUT` requests to
    update data for single objects.

    .. sourcecode:: python

        from arrested import Api, ObjectResource

        class UserObjectApi(Api, ObjectResource):

            url = '/users/<string:obj_id>'
            endpoint_name='users.object'
            request_handler = KimRequestHandler
            methods = ['GET']
            id_param_name = 'obj_id'

            def get_object(self):

                return get_user_by_id(self.kwargs[self.id_param_name])

    Users must provide a :py:class:`ResponseHandler` to accept GET requests
    with ObjectResource endpoints.

    .. seealso:
        :meth:`get`

    """

    def get_update_response(self, status=200):
        """Called by :meth:`put` to process an object and return
        a valid json response.

        This method can be overriden to provide your own flavour of response
        generation where required but typically this is done by implementing
        custom :py:class:`ResponseHandler`.

        :param status: The HTTP status code returned with the response

        .. seealso:
            :meth:`make_response`
        """
        self.response = \
            self.get_response_handler(**self.get_update_response_params())
        self.response.process(data=self.obj)

        return (self.make_response(self.response.data, status=status))

    def get_update_request_params(self, **params):

        params = self.get_request_handler_params(**params)
        params['role'] = self.marshal_role

        return params

    def get_update_response_params(self, **params):

        params = self.get_request_handler_params(**params)
        params['role'] = self.serialize_role

        return params

    def update_object(self):
        """TODO(mike) Docs
        """
        session = self.get_session()
        session.add(self.obj)
        session.commit()

    def put(self, *args, **kwargs):
        """Handles a PUT request for a resource updates a single object.

        A :class:`.handlers.ResponseHandler` and
        :class`.handlers.RequesHandler`is required to accept PUT
        requests.

        Users must also define the :meth:`update_object` which returns an
        object that will be serialized by the `reponse_handler`.
        This is typically done using a :py:class:`ObjectMixin` provided or
        by a custom mixin.

        UpdateableResource resources also require `get_object` be
        implemented.  This object will be the object that gets updated
        with the data from the PUT request.

        This Resource would typically be used in conjunction with
        :class:`.ObjectResource` and therefore get_object would
        be implemented .

        This method will itself call the :meth:`get_update_response` method
        where the response handler will actually process the object returned
        from :meth:`get_object`

        .. seealso:
            :meth:`get_update_response`
        """

        self.request = \
            self.get_request_handler(**self.get_update_request_params())

        self.obj = \
            self.request.process(
                self.get_data(), instance=self.get_object()).data

        if self.request.errors is not None:

            return self.on_errors(self.request.errors, status=400)

        self.update_object()

        return self.get_update_response()


class DeleteableResource(HttpResource, ModelMixin):

    def get_delete_response(self, status=204):
        """Called by :meth:`put` to process an object and return
        a valid json response.

        This method can be overriden to provide your own flavour of response
        generation where required but typically this is done by implementing
        custom :py:class:`ResponseHandler`.

        :param status: The HTTP status code returned with the response

        .. seealso:
            :meth:`make_response`
        """

        return (self.make_response('', status=status))

    def delete_object(self):
        """TODO(mike) Docs
        """
        session = self.get_session()
        session.delete(self.obj)
        session.commit()

    def delete(self, *args, **kwargs):
        """Handles a PUT request for a resource updates a single object.

        A :class:`.handlers.ResponseHandler` and
        :class`.handlers.RequesHandler`is required to accept PUT
        requests.

        Users must also define the :meth:`update_object` which returns an
        object that will be serialized by the `reponse_handler`.
        This is typically done using a :py:class:`ObjectMixin` provided or
        by a custom mixin.

        UpdateableResource resources also require `get_object` be
        implemented.  This object will be the object that gets updated
        with the data from the PUT request.

        This Resource would typically be used in conjunction with
        :class:`.ObjectResource` and therefore get_object would
        be implemented .

        This method will itself call the :meth:`get_update_response` method
        where the response handler will actually process the object returned
        from :meth:`get_object`

        .. seealso:
            :meth:`get_update_response`
        """
        self.obj = self.get_object()

        self.delete_object()

        return self.get_delete_response()
