from flask import Blueprint


__all__ = ['Resource']


class Resource(Blueprint):
    """Resource extends Flasks existing Blueprint object and provides some utilty methods
    that make registering :class:`Endpoint` simpler.
    """

    def __init__(
            self, name, import_name, api=None, before_all_hooks=None,
            after_all_hooks=None, *args, **kwargs):
        """Construct a new Reosurce blueprint.  In addition to the normal Blueprint
        options, Resource accepts kwargs to set request middleware.

        :param api: API instance being the resource is being registered against.
        :param before_all_hooks: A list of middleware functions that will be applied
            before every request.
        :param after_all_hooks: A list of middleware functions that will be applied
            after every request.

        Middleware
        ~~~~~~~~~~~~~

        Arrested supports applying request middleware at every level of the application
        stack.  Resource middleware will be applied for every Endpoint registered on
        that Resource.

        .. code-block:: python

            character_resource = Resource(
                'characters', __name__,
                url_prefix='/characters',
                before_all_hooks=[log_request]
            )

        Arrested request middleware works differently from the way Flask middleware does.
        Middleware registered at the Resource and API level are consumed by the
        :meth:`arrested.Endpoint.dispatch_request` rather than being fired via the Flask
        app instance.  This is so we can pass the instance of the endpoint handling the
        request to each piece of middleware registered on the API or Resource.

        .. code-block:: python

            def api_key_required(endpoint):

                if request.args.get('api_key', None) is None:
                    endpoint.return_error(422)
                else:
                    get_client(request.args['api_key'])

            character_resource = Resource(
                'characters', __name__,
                url_prefix='/characters',
                before_all_hooks=[api_key_required]
            )

        Please note, Flask's normal App and Blueprint middleware can still be used
        as normal, it just doesn't recieve the instance of the endpoint registered to
        handle the request.

        """

        self.before_all_hooks = before_all_hooks or []
        self.after_all_hooks = after_all_hooks or []

        super(Resource, self).__init__(name, import_name, *args, **kwargs)
        if api is not None:
            self.init_api(api)

    def init_api(self, api):
        """Registered the instance of :class:`arrested.ArrestedAPI` the :class:`Resource`
        is being registered against.

        :param api: API instance being the resource is being registered against.
        """
        self.api = api

    def add_endpoint(self, endpoint):
        """Register an :class:`Endpoint` aginst this resource.

        :param endpoint: :class:`Endpoint` API Endpoint class

        Usage::

            foo_resource = Resource('example', __name__)
            class MyEndpoint(Endpoint):

                url = '/example'
                name = 'myendpoint'

            foo_resource.add_endpoint(MyEndpoint)
        """

        if self.url_prefix:
            url = '{prefix}{url}'.format(prefix=self.url_prefix, url=endpoint.url)
        else:
            url = endpoint.url

        self.add_url_rule(
            url,
            view_func=endpoint.as_view(endpoint.get_name()),
        )
