.. _quickstart:

Quickstart
===========

.. module:: arrested

Eager to get going? This page gives an introduction to getting started
with Flask-Arrested.

First, make sure that:

* Arrested is :ref:`installed <install>`

This tutorial steps through creating a simple Star Wars themed REST API using Arrested.  We assume you have a working knowledge of both Python and Flask.
The example app uses the following additional libraries

* SQLAlchemy
* Flask-SQLAlchemy
* Kim

Please note that Arrested can be used with any flavour of data store or preferred way of marshaling and serializing data.  These are just used as a common example.

You can find the example application `here <https://github.com/oldstlabs/flask-arrested/tree/master/example>`_.


APIs, Resources and Endpoints - Defining your first API
-------------------------------------------------------------

Flask-Arrested is split into 3 key concepts.  :class:`ArrestedAPI`'s, :class:`Resource` and :class:`Endpoint`.  API's contian multiple Resources.  For example
Our API will contain a Characters resource, a Planets resource and so on.  Resources are a collection of Endpoints.  Endpoints define
the urls inside of our Resources ``/v1/charcaters`` ``/v1/planets/hfyf66775gjgjjf`` etc.

.. note::

    To follow along with the example you will need to install Docker for your operating system.  Find out how here.

.. code-block:: python

    from flask import Flask

    from arrested import ArrestedAPI, Resource
    from arrested.contrib.sql_alchemy import (
        DBListMixin,
        DBCreateMixin,
        DBObjectMixin,
    )
    from arrested.contrib.kim_arrested import KimEndpoint

    from example.models import db, Character
    from example.mappers import CharacterMapper


    app = Flask(__name__)
    api_v1 = ArrestedAPI(app, url_prefix='/v1')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/code/example/starwars.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    characters_resource = Resource('characters', __name__, url_prefix='/characters')


    class CharactersIndexEndpoint(KimEndpoint, DBListMixin, DBCreateMixin):

        name = 'list'
        many = True
        mapper_class = CharacterMapper

        def get_query(self):

            return db.session.query(Character)


    class CharacterObjectEndpoint(KimEndpoint, DBObjectMixin):

        name = 'object'
        url = '/<string:obj_id>'
        mapper_class = CharacterMapper
        model = Character

        def get_query(self):

            return db.session.query(Character)


    characters_resource.add_endpoint(CharactersIndexEndpoint)
    characters_resource.add_endpoint(CharacterObjectEndpoint)
    api_v1.register_resource(characters_resource)


Start the Docker container in the example/ directory.

.. code-block:: shell

    $ docker-compose run --rm --service-ports api

Hit the ``http://localhost:5000/v1/characters`` url in your browser.  You will see the JSON response
for the characters endpoint returned.

There's a lot going on here, let's recap.

* We have now got an API that returns a list of serialized character objects via the /v1/characters endpoint.
* We can create new character objects by making a POST request to /v1/characters
* We can fetch a character by making a GET request to /v1/characters/1
* We can update an existing character by making a PUT request to /v1/characters/1
* We can delete a character by making a DELETE request to /v1/characters/1
* Our Database objects are being automatically serialzied using the Kim Mapper we defined

All in around 50 lines of code!  Try making some other requests using curl to add new characters or update Obe Wan.


Getting objects
^^^^^^^^^^^^^^^^

Our example API is using the SQLAlchemy integration.  In our CharactersListEndpoint we use the DBListMixin.  All we needed to do for our Characters to be returned
from the API was provide the :meth:`arrested.contrib.sql_alchemy.DBListMixin.get_query`.  The :class:`arrested.contrib.sql_alchemy.DBListMixin` implements the :class:`arrested.mixins.GetListMixin`.  This class
expects the :meth:`arrested.mixins.GetListMixin.get_objects` to be implemented.

If you wanted special handling for fetching objects from a different datastore or you need to apply some further processing to your database objects, you could simply override :meth:`arrested.mixins.GetListMixin.get_objects` and do the work there.

.. code-block:: python

    def get_objects(self, obj):

        return get_objects_from_data_store()

Saving objects
^^^^^^^^^^^^^^^^

The DBCreateMixin automatically handles persisting our new Character objects back to the database.  If we wnated to do some additional processing on the object before the session is committed we could simply override the :meth:`arrested.mixins.CreateMixin.save_object` which the :class:`arrested.contrib.sql_alchemy.DBCreateMixin` implements.

.. code-block:: python

    def save_object(self, obj):

        obj.created_by = self.get_user()
        return super(CharactersListEndpoint, self).save_object(obj)


Updating objects
^^^^^^^^^^^^^^^^^

Deleting objects
^^^^^^^^^^^^^^^^^


Middleware
-------------------

Flask comes with a great system for handling middleware.  Arrested builds on top of this system to allow more fine grained control of where and when your middleware is run
when requests are being made to your APIs.

API Middleware
^^^^^^^^^^^^^^^^^

Middleware can be applied at each level of the API.  You will often want a peice middleware to be applied across every resource and every endpoint defined in an API.  An example of this might be authentication.
The :class:`ArrestedAPI` object supports two middleware hooks, ``before_all_hooks`` and ``after_all_hooks``. Let's create a basic example that demonstrates how authentication can be applied across APIs.


.. code-block:: python

    def authenticated(endpoint):
        token_valid = request.args.get('token') == 'test-token'
        if not token_valid:
            endpoint.return_error(401)

    api_v1 = ArrestedAPI(app, url_prefix='/v1', before_all_hooks=[authenticated])


Hit the ``http://localhost:5000/v1/characters`` url in your browser. We should now get a 401 status code back when requesting the characters API.
A second request, this time providng our API token should return our character objects. ``http://localhost:5000/v1/characters?token=test-token``

Resource Middleware
^^^^^^^^^^^^^^^^^^^^^

Middleware can also be applied on a per Resource basis. :class:`Resource`, Like the :class:`ArrestedAPI` object also has two options for injecting middleware into the request/response cycle.  ``before_all_hooks`` and ``after_request_hook``.  Let's add some logging code to our characters resource using an after request hook.


.. code-block:: python

    def log_request(endpoint, response):

        app.logger.debug('request to characters resource made')
        return response

    characters_resource = Resource('characters', __name__, url_prefix='/characters', after_all_hooks=[log_request])

Our middleware is slightly different from the authenication example.  When we're dealing with an after request hook we are also passed the response object as well as the endpoint instance.  The response object should be returned
from every after hook defined on our APIs and Resources.

Endpoint Middleware
^^^^^^^^^^^^^^^^^^^^^

Lastly we come to the :class:`Endpoint` object.  :class:`Endpoint` supports defining middleware using the following hooks:

* before_all_hooks
* before_get_hooks
* after_get_hooks
* before_post_hooks
* after_post_hooks
* before_put_hooks
* after_put_hooks
* before_patch_hooks
* after_patch_hooks
* before_delete_hooks
* after_delete_hooks
* after_all_hooks

As you can see, not only can we dfine the before_all_hooks and after_all_hooks like we have on the :class:`ArrestedAPI` and :class:`Resource`, we can also inject middleware before and after each http method.
Let's update our CharacterObjectEndpoint to require an admin for PUT requests.

.. code-block:: python

    def is_admin(endpoint):

        endpoint.return_error(403)

    class CharacterObjectEndpoint(KimEndpoint, DBObjectMixin):

        name = 'object'
        url = '/<string:obj_id>'
        mapper_class = CharacterMapper
        model = Character
        before_put_hooks = [is_admin]

        def get_query(self):

            return db.session.query(Character)


Making a PUT request to ``http://localhost:5000/v1/characters/1`` using curl will now return a 403


Handling Requests and Responses
--------------------------------

For the sake of the quickstart being, well, quick we're making use of the provided integrations for Kim and SQLAlchemy.  These contrib modules are doing a lot of work for us.
The advanced documentation goes into more detail about these topics but I felt it was important to surface a least the fundamentals of how Arrested handles incoming requests and generates responses.

:class:`Endpoint` requires that a :class:`ResponseHandler` and :class:`RequestHandler` be set.  These classes define a standard interface for processing data into and out from your API.  In our example API we use the :class:`arrested.contrib.kim.KimEndpoint` class
which sets up everything we need to have Kim serialize and marshal our data.

:class:`ResponseHandler` and :class:`RequestHandler` gives users complete flexability over how data is handled.  You could have one library dealing with data in and and another that handles serialization - even mixing different libraries for different endpoints.  As long as the Handler interface has been implemented these classes
can do whatever you like.

You can read more about these topcis in depth in the advanced documentation.

:ref:`Request and Response handling <advanced_request_response_handling>`.
