Setting up the arrested App object
======================================

The Arrested app object is used as a sort of Flask Blueprint object with some specifics
for your api.   You should consider each instance of the :class:`arrested.app.Arrested` object
as a single version available in your RESTFul api.

The Arrested class provides the typical flask appliaction initialisation api.

Instantiating the Arrested object can be done in one of two ways.  You
may pass the :class:`flask.Flask` application object
to the construtor

.. sourcecode:: python

    from flask import Flask
    from arrested import Arrested

    app = Flask(__name__)
    api = Arrested(app)

    api.register(UserIndexApi)

Or the flask application object may be lazily loaded.  This is useful when
users make use of the factory method for generating flask objects.

You might define all your Api Resources in a module called `myproject.api`

.. sourcecode:: python

    from arrested import Arrested, Api

    api = Arrested()

    class UserIndexApi(Api):

        url = '/users'

    api.regsiter(UserIndexApi)


In our flask factory function we'd simply need to import the api object
and register it with our flask app object using ``api.init_app()`` method.

.. sourcecode:: python

    from flask import Flask

    from myproject.api import api

    def create_app(config_name='dev'):
        app = Flask(__name__)
        api.init_app(app)

        return app


Registering Api endpoints.
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once an Arrested App instance has been defined you can start to register the endpoints available for your Api.
Defning api and Resource are covered in more detail !!!!!HERE!!!!!.

.. sourcecode:: python

    from arrested import Arrested

    from myproject.api import UserIndexApi, MyOtherApi

    api = Arrested(name='my_api')
    api.register(UserIndexApi)
    api.register(MyOtherApi, url='/override/url')


Api versioning.
~~~~~~~~~~~~~~~~~~

The Arrested object accepts a version parameter which is used when building the urls to your api endpoints.
Simply pass the `url_prefix` option to the Arrested object to have all the endpoints registered on this api with that prefix

.. sourcecode:: python

    from arrested import Arrested
    from myproject.api.v1 import UserIndexApiV1
    from myproject.api.v2 import UserIndexApiV2

    api_v1 = Arrested(url_prefix='/v1')
    api_v2 = Arrested(url_prefix='/v2')


The url_prefixing can be disabled by passing None to the Arrested instance.

.. sourcecode:: python

    from arrested import Arrested

    api = Arrested(url_prefix=None)


.. seealso::
    :meth:`arrested.app.Arrested.get_api_url`


Api naming.
~~~~~~~~~~~~~~~~~~

Like Flask's Blueprint object, :py:class:`arrested.app.Api` objects accept a name parameter which is then used with
Flasks routing system.

The name is used to name space url routes when using flask utility functions like `url_for`

.. sourcecode:: python

    from arrested import Arrested

    class UserIndexApi(IndexApi):

        endpoint_name = 'users.index'

    api = Arrested(name='my_api')
    api.register(UserIndexApi)

    url_for('my_api.users.index')


Api endpoints are registered using a combination of Arrested.name and Resource.endpoint_name
