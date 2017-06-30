

__all__ = ['ArrestedAPI']


class ArrestedAPI(object):
    """ArrestedAPI defines versions of your api which :class:`Endpoint` are registered
    against.  It acts like ``Flasks``  Blueprint object with a few minor differences.

    """

    def __init__(self, app=None, url_prefix='', before_all_hooks=None,
                 after_all_hooks=None):
        """Constructor to create a new ArrestedAPI object.

        :param app: Flask app object.
        :param url_prefix: Specify a url prefix for all resources attached to this API.
            Typically this is used for specifying the API version.
        :param before_all_hooks: A list containing funcs which will be called before
            every request made to any resource registered on this Api.
        :param after_all_hooks: A list containing funcs which will be called after
            every request made to any resource registered on this Api.

        Usage::

            app = Flask(__name__, url_prefix='/v1')
            api_v1 = ArrestedAPI(app)

        .. seealso::
            :meth:`arrested.api.ArrestedAPI.init_app`
        """

        self.before_all_hooks = before_all_hooks or []
        self.after_all_hooks = after_all_hooks or []
        self.url_prefix = url_prefix
        self.deferred = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialise the ArrestedAPI object by storing a pointer to a Flask app object.
        This method is typically used when initialisation is deferred.

        :param app: Flask application object

        Usage::

            app = Flask(__name__)
            ap1_v1 = ArrestedAPI()
            api_v1.init_app(app)
        """

        self.app = app
        if self.deferred:
            self.register_all(self.deferred)

    def register_resource(self, resource, defer=False):
        """Register a :class:`arrested.resource.Resource` blueprint object against with
        the Flask app object.

        :param resource: :class:`arrested.resource.Resource` or :class:`flask.Blueprint`
            object.
        :param defer: Optionally specify that registering this resource should be
            deferred.  This option is useful when users are creating their
            Flask app instance via a factory.

        Deferred resource registration
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        Resources can optionally be registered in a deferred manor.  Simply pass
        `defer=True` to :meth:`ArrestedAPI.register_resource` to attach the resource to
        the API without calling register_blueprint.

        This is useful when you're using the factory pattern for creating your Flask app
        object as demonstrated below. Deferred resource will not be registered until the
        ArrestedAPI instance is initialised with the Flask app object.

        Usage::

            api_v1 = ArrestedAPI(prefix='/v1')
            characters_resource = Resource(
                'characters', __name__, url_prefix='/characters'
            )
            ap1_v1.register_resource(characters_resource, defer=True)

            def create_app():

                app = Flask(__name__)
                api_v1.init_app(app) # deferred resources are now registered.
        """
        if defer:
            self.deferred.append(resource)
        else:
            resource.init_api(self)
            self.app.register_blueprint(resource, url_prefix=self.url_prefix)

    def register_all(self, resources):
        """Register each resource from an iterable.

        :params resources: An iterable of :class:`arrested.Resource` objects

        Usage::
            characters_resource = Resource(
                'characters', __name__, url_prefix='/characters'
            )
            planets_resource = Resource('planets', __name__, url_prefix='/planets')
            api_v1 = ArrestedAPI(prefix='/v1')
            api_v1.register_all([characters_resource, planets_resource])
        """
        for resource in resources:
            self.register_resource(resource)
