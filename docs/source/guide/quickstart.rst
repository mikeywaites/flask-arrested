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

Example Application
--------------------

The examples used in this guide can be found here `<https://github.com/oldstlabs/flask-arrested/tree/master/example>`_.

.. note::

    To follow along with the example you will need to install Docker for your operating system.  Find out how here `<https://docker.com>`_.


APIs, Resources and Endpoints - Defining your first API
-------------------------------------------------------------

Flask-Arrested is split into 3 key concepts.  :class:`.ArrestedAPI`'s, :class:`.Resource` and :class:`.Endpoint`.  API's contian multiple Resources.  For example
Our API will contain a Characters resource, a Planets resource and so on.  Resources are a collection of Endpoints.  Endpoints define
the urls inside of our Resources ``/v1/charcaters`` ``/v1/planets/hfyf66775gjgjjf`` etc.

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
from the database via our API was provide the :meth:`get_query <arrested.contrib.sql_alchemy.DBListMixin.get_query>` method.  The :class:`DBListMixin <arrested.contrib.sql_alchemy.DBListMixin>` implements the :class:`.GetListMixin` interface.  This class
expects the :meth:`.GetListMixin.get_objects` method to be implemented.

If you wanted special handling for fetching objects from a different datastore or you need to apply some further processing to your database objects, you could simply override :meth:`get_objects <arrested.mixins.GetListMixin.get_objects>` and do the work there.  Below is an example of a custom endpoint that implements the :class:`.GetListMixin` interface.

.. code-block:: python

    import redis
    from arrested import Endpoint, GetListMixin

    class CustomEndpoint(Endpoint, GetListMixin):

        many = True
        name = 'list'

        def get_objects(self, obj):

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news')

Saving objects
^^^^^^^^^^^^^^^^

The :class:`DBCreateMixin <arrested.contrib.sql_alchemy.DBCreateMixin>` automatically handles persisting our new Character objects back to the database.  If we wanted to do some additional processing on the object before the session was committed or we needed some custom logic for our endpoint we simply override the :meth:`.CreateMixin.save_object` which the :class:`DBCreateMixin <arrested.contrib.sql_alchemy.DBCreateMixin>` implements.  Below is an example of a custom endpoint that implements the :class:`.CreateMixin` interface and saves our data in redis.

.. code-block:: python

    import redis
    from arrested import Endpoint, GetListMixin, CreateMixin

    class CustomEndpoint(Endpoint, GetListMixin, CreateMixin):

        many = True
        name = 'list'

        def get_objects(self, obj):

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news')

        def save_object(self, obj):

            # obj will be a dict here as we're using the default RequestHandler
            return r.hmset('news', obj)


Object Endpoints
^^^^^^^^^^^^^^^^^

Object endpoints are allow you to define APIS that let your uses GET, PUT, PATCH and DELETE single objects.  The :class:`DBObjectMixin <arrested.contrib.sql_alchemy.DBObjectMixin>` mixin we used
with our CharacterObjectEndpoint implements several methods that provide us with everything we need to work with a specific character object.

The Mixins can be combined to provide support for all the typical HTTP methods used when working with a single object.
Regardless of the HTTP methods your supporting against your object endpoints the :meth:`.ObjectMixin.get_object` is always required.


Getting a single object
^^^^^^^^^^^^^^^^^^^^^^^^

:class:`DBObjectMixin <arrested.contrib.sql_alchemy.DBObjectMixin>` implements the :class:`.GetObjectMixin` interface.  It automatically handles filtering the query returned by the :meth:`DBObjectMixin.get_query <arrested.contrib.sql_alchemy.DBObjectMixin.get_query>` by id.  As we've seen in the examples above we can implement
cutom logic as required to handle pretty much any use case.  Here's a custom Endpoint that fetches a specific object from redis using the id passed as part of the url.

.. code-block:: python

    import redis
    from arrested import Endpoint, GetObjectMixin

    class CustomEndpoint(Endpoint, GetObjectMixin):

        url = '/<str:obj_id>'
        name = 'object'

        def get_object(self, obj):

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news')


Updating an object
^^^^^^^^^^^^^^^^^^^

:class:`DBObjectMixin <arrested.contrib.sql_alchemy.DBObjectMixin>` implements the :class:`.PutObjectMixin` interface.  The :meth:`.PutObjectMixin.update_object` method is overridden to persist our updated object back to the database.  As in the previous examples, this interface can be implemented to provide custom logic as required.  Here's
a simple example that updates an existing object in a redis set.


.. code-block:: python

    import redis
    from arrested import Endpoint, PutObjectMixin

    class CustomEndpoint(Endpoint, PutObjectMixin):

        url = '/<str:obj_id>'
        name = 'object'

        def get_object(self, obj):

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news')

        def update_object(self, obj):

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmset('news')

When the PUT request is handled by our CustomEndpoint the :meth:`.ObjectMixin.get_object` method is called first to retrieve the existing object.  If an object is found
the :meth:`.PutObjectMixin.update_object` is then called.

To support updating objects via PATCH requests all we need to do is use the :class:`.PatchObjectMixin`.  It works in very much the same way as :class:`.PutObjectMixin` except that we the :meth:`.PatchObjectMixin.patch_object` method is called.


.. code-block:: python

    import redis
    from arrested import Endpoint, PutObjectMixin, PatchObjectMixin

    class CustomEndpoint(Endpoint, PutObjectMixin, PatchObjectMixin):

        url = '/<str:obj_id>'
        name = 'object'

        def get_object(self, obj):

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news')

        def do_update(self, obj):

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmset('news')

        def update_object(self, obj):

            self.do_update(obj)

        def patch_object(self, obj):

            self.do_update(obj)


Deleting objects
^^^^^^^^^^^^^^^^^

The last operation to cover is deleteing objects.  :class:`DBObjectMixin <arrested.contrib.sql_alchemy.DBObjectMixin>` overrides the :meth:`.DeleteObjectMixin.delete_object` method to automatically remove the object from the database.  We can override this as we've seen previously to provide custom logic.
As we saw with the put and patch mixins we must implement the :meth:`ObjectMixin.get_object` method as well as :meth:`.DeleteObjectMixin.delete_object`.

.. code-block:: python

    import redis
    from arrested import Endpoint, DeleteObjectMixin

    class CustomEndpoint(Endpoint, DeleteObjectMixin):

        url = '/<str:obj_id>'
        name = 'object'

        def get_object(self, obj):

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news')

        def delete_object(self, obj):

            return r.delete('news')


Middleware
-------------------

Flask comes with a great system for handling middleware.  Arrested builds on top of this system to allow more fine grained control of where and when your middleware is run
when requests are being made to your APIs.

API Middleware
^^^^^^^^^^^^^^^^^

Middleware can be applied at each level of the API.  You will often want a peice middleware to be applied across every resource and every endpoint defined in an API.  An example of this might be authentication.
The :class:`.ArrestedAPI` object supports two middleware hooks, ``before_all_hooks`` and ``after_all_hooks``. Let's create a basic example that demonstrates how authentication can be applied across APIs.


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

Middleware can also be applied on a per Resource basis. :class:`.Resource`, Like the :class:`.ArrestedAPI` object also has two options for injecting middleware into the request/response cycle.  ``before_all_hooks`` and ``after_request_hook``.  Let's add some logging code to our characters resource using an after request hook.


.. code-block:: python

    def log_request(endpoint, response):

        app.logger.debug('request to characters resource made')
        return response

    characters_resource = Resource('characters', __name__, url_prefix='/characters', after_all_hooks=[log_request])

Our middleware is slightly different from the authenication example.  When we're dealing with an after request hook we are also passed the response object as well as the endpoint instance.  The response object should be returned
from every after hook defined on our APIs and Resources.

Endpoint Middleware
^^^^^^^^^^^^^^^^^^^^^

Lastly we come to the :class:`.Endpoint` object.  :class:`.Endpoint` supports defining middleware using the following hooks:

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

As you can see, not only can we dfine the before_all_hooks and after_all_hooks like we have on the :class:`.ArrestedAPI` and :class:`.Resource`, we can also inject middleware before and after each http method.
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


Request Handling
^^^^^^^^^^^^^^^^^

HTTP requests that process data require that a :class:`.RequestHandler` be defined on the Endpoint using the request_handler property.  The default :class:`.RequestHandler` simply pulls the json data from the Flask request, deserialises it into a dict and returns it verbatim.  Let's suppose we want to apply some **very** basic validation ensuring that certain keys are present within the request payload.
To do this we will implement a custom :class:`.RequestHandler` that takes a list of field names and ensures all the keys are present.


.. code-block:: python

    from arrested.handlers import RequestHandler

    class ValidatingRequestHandler(RequestHandler):

        def __init__(self, endpoint, fields=None, *args, **kwargs):

            super(ValidatingRequestHandler, self).__init__(endpoint, *args, **params)
            self.fields = fields

        def handle(self, data, **kwargs):

            if self.fields and not sorted(data.keys()) == sorted(self.fields):
                payload = {
                    "message": "Missing required fields",
                }
                self.endpoint.return_error(422, payload=payload)

            return super(ValidatingRequestHandler, self).handle(data, **kwargs)


    class CustomEndpoint(Endpoint, GetListMixin, CreateMixin):

        many = True
        name = 'list'
        request_handler = ValidatingRequestHandler

        def get_objects(self, obj):

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news')

        def save_object(self, obj):

            # obj will be a dict here as we're using the default RequestHandler
            return r.hmset('news', obj)

        def get_request_handler_params(self, **params):

            params = super(KimEndpoint, self).get_request_handler_params(**params)
            params['fields'] = ['field_one', 'field_two']

            return params


This simple examples demonstrates the flexibility the handler system offers.  We can define handlers to accomodate for any user case imaginable in python.  We can use the :meth:`.Endpoint.get_request_handler_params` to configure the handler
on an endpoint by endpoint basis.  We can even have different handlers handling different requests on each Endpoint.

Accessing the Request object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We've seen how to define a custom handler and how we configure it to process incoming data to our Endpoint.  So what does arrested do with all this stuff?  Whenever a POST, PUT, PATCH request is made to one of your :class:`.Endpoint` arrested will instantiate the ``request`` object and set it on the Endpoint.
This allows users to later access the handler instance used to process the incoming request.  An example of this in practice is the :meth:`CreateMixin.handle_post_request` method.

.. code-block:: python

    def handle_post_request(self):
        """Handle incoming POST request to an Endpoint and marshal the request data
        via the specified RequestHandler.  :meth:`.CreateMixin.save_object`. is then
        called and must be implemented by mixins implementing this interfce.

        .. seealso::
            :meth:`CreateMixin.save_object`
            :meth:`Endpoint.post`
        """
        self.request = self.get_request_handler()
        self.obj = self.request.process().data

        self.save_object(self.obj)
        return self.create_response()


Response Handling
^^^^^^^^^^^^^^^^^^

Endpoints that return data will typically require that a :class:`.ResponseHandler` be defined on the Endpoint using the response_handler property.  The default :class:`.ResponseHandler` simply attempts to serialize the obj passed to it using ``json.dumps``.
This works fine in simple cases but when we're dealing with more complex types like SQLAlchemy Models we need something a bit smarter.  In the example application we use the KimResponseHandler.

Let's look at implementing a simple :class:`.ResponseHandler` that removes some fields from response data.


.. code-block:: python

    from arrested.handlers import RequestHandler

    class ValidatingResponseHandler(RequestHandler):

        def __init__(self, endpoint, fields=None, *args, **kwargs):

            super(ValidatingRequestHandler, self).__init__(endpoint, *args, **params)
            self.fields = fields

        def handle(self, data, **kwargs):

            new_data = {}
            for key, value in data.items():
                if key in self.fields:
                    new_data[key] = value

            return super(ValidatingResponseHandler, self).handle(new_data, **kwargs)


    class CustomEndpoint(Endpoint, GetListMixin, CreateMixin):

        many = True
        name = 'list'
        response_handler = ValidatingResponseHandler

        def get_objects(self, obj):

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news')

        def save_object(self, obj):

            # obj will be a dict here as we're using the default RequestHandler
            return r.hmset('news', obj)

        def get_response_handler_params(self, **params):

            params = super(KimEndpoint, self).get_response_handler_params(**params)
            params['fields'] = ['field_one', ]

            return params


Accessing the Response object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As we saw with the Request object, Arrested will store the response handler instance against a property on the Endpoint called ``response``.  This can be accessed later to apply additional processing and that sort of thing.
By default a ResponseHandler is created for any request handled by an Endpoint.  This means that the data generated by a RequestHandler will later be processed and returned by the provided ResponseHandler.  We can see this in action in the :class:`.PutObjectMixin` mixin shown below.

.. code-block:: python

    class PutObjectMixin(HTTPMixin, ObjectMixin):
        """Base PutObjectMixins class that defines the expected API for all PutObjectMixin
        """

        def object_response(self, status=200):
            """Generic response generation for Endpoints that return a single
            serialized object.

            :param status: The HTTP status code returned with the response
            :returns: Response object
            """

            self.response = self.get_response_handler()
            self.response.process(self.obj)
            return self._response(self.response.get_response_data(), status=status)

        def put_request_response(self, status=200):
            """Pull the processed data from the response_handler and return a response.

            :param status: The HTTP status code returned with the response

            .. seealso:
                :meth:`ObjectMixin.object_response`
                :meth:`Endpoint.handle_put_request`
            """

            return self.object_response(status=status)

        def handle_put_request(self):
            """
            """
            obj = self.obj
            self.request = self.get_request_handler()
            self.request.process()

            self.update_object(obj)
            return self.put_request_response()

        def update_object(self, obj):
            """Called by :meth:`PutObjectMixin.handle_put_request` ater the incoming data has
            been marshalled by the RequestHandler.

            :param obj: The marhsaled object from RequestHandler.
            """
            return obj


You can read more about these topcis in depth in the advanced documentation.

:ref:`Request and Response handling <advanced_request_response_handling>`.
