Handlers
=================

.. _handlers:

Arrested Request and Response handlers are responsible for how your endpoints marshal and serialize data.  They are a simple interface to your choosen data handling methods
and allow you to make choices, on an api by api basis, about how your data is processed.


Each Arrested Api may define a ``request_handler`` and a ``response_handler``, depending on the Resources used these may be required.


.. sourcecode:: python

    from arrested import Arrested, Api
    from arrested.api import ListableResource


    class UserIndexApi(Api, ListableResource):
        url = '/users'
        endpoint_name = 'users.index'
        methods = ['GET', ]
        response_handler = MyResponseHandler

        def get_objects(self):
            return get_users()


The api above makes use of the :class:.`ListableResource` which requires that a ``response_handler`` is present.  Below is an example of a custom response handler
taken from the ``arrested.contrib.kim`` module.

Request and Response handlers simply implement their custom logic in the handle method.

.. sourcecode:: python

    class KimHandler(Handler):

        def __init__(self, *args, **params):
            super(KimHandler, self).__init__(*args, **params)

            self.mapper_class = params.pop('mapper_class', None)
            self.mapper_kwargs = params.pop('mapper_kwargs', {})
            self.role = params.pop('role', '__default__')
            self.many = params.pop('many', False)
            self.raw = params.pop('raw', False)

        @property
        def mapper(self):
            if self.mapper_class is None:
                raise Exception('KimHandler requires a Kim mapper_class')

            return self.mapper_class


    class KimResponseHandler(KimHandler):

        def handle(self, data):

            if self.many:
                return self.mapper.many(raw=self.raw, **self.mapper_kwargs) \
                    .serialize(data, role=self.role)
            else:
                return self.mapper(obj=data, raw=self.raw, **self.mapper_kwargs) \
                    .serialize(role=self.role)


.. seealso::
    :class:`.Handler`

    :class:`.Resource`


Using Handlers
~~~~~~~~~~~~~~~~~~~~~~~~

Arrested Resources typically provide everything needed for the request and response handlers to run.  Here's an example of how the :class:`.ListableResource` handles
a GET request invoking the ``response_handler``

.. sourcecode:: python

    def get(self, *args, **kwargs):
        if not hasattr(self, 'get_objects'):
            raise NotImplementedError('Please implement the get_objects')

        self.response = self.get_response_handler()

        self.objects = self.get_objects()

        self.response.process(self.objects)

        return self.get_list_response()

The response handler instance is stored on the Resource using the property ``response``.  This property is then available for use throughout the life-cycle of the request.
The ``response_handler`` instance below is later used in the get_list_response method to return the serialized data as a JSON string.

.. sourcecode:: python

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

Request handlers operate in much the same way, the instance of the ``request_handler`` will be stored on using a property called ``request``.
Here's an example of how :class:`.CreateableResource` handles a POST request.

.. sourcecode:: python

    def post(self, *args, **kwargs):
        if not hasattr(self, 'get_data'):
            raise NotImplementedError('Please implement the get_data method')

        self.request = self.get_request_handler()

        self.request.process(self.get_data())

        self.save_object()

        return self.get_create_response()


.. seealso::
    :class:`.Handler`

    :class:`.Resource`


Handling errors
~~~~~~~~~~~~~~~~~~~~~~~~

In some cases your Handlers will need to react to errors IE when validation errors occur during marshaling.  The Request handler below taken from the kim contrib module is an examle of this.
Your handle simple needs to set errors property, in this case a dict of field-error messages, and the Resources calling these methods will act accordingly.

.. sourcecode:: python

    class KimRequestHandler(KimHandler):

        def handle(self, data):

            try:
                if self.many:
                    return self.mapper.many(raw=self.raw, **self.mapper_kwargs) \
                        .marshal(data, role=self.role)
                else:
                    return self.mapper(data=data, raw=self.raw, **self.mapper_kwargs) \
                        .marshal(role=self.role)
            except MappingInvalid as e:
                self.errors = e.errors


Configuring your Handlers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you handlers are instantiated they will be called with kwargs provided by the :meth:`.Resource.get_request_handler_params` and the :meth:`.Resource.get_response_handler_params` methods.  To pass specific options to your chosen request/response handlers simply subclass these methods and return
the required config.

.. sourcecode:: python

    from arrested import Arrested, Api
    from arrested.api import ListableResource


    class UserIndexApi(Api, ListableResource, CreateableResource):
        url = '/users'
        endpoint_name = 'users.index'
        methods = ['GET', 'POST']
        response_handler = MyResponseHandler
        request_handler = MyResponseHandler

        def get_request_handler_params(self, **params):
            params = super(UserIndexApi, self) \
                .get_request_handler_params(**params)
            params['form'] = MyForm

            return params

        def get_response_handler_params(self, **params):
            params = super(UserIndexApi, self) \
                .get_request_handler_params(**params)
            params['form'] = MyForm

            return params

        def get_objects(self):
            return get_users()
