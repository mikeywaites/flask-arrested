.. _quickstart:

Guide
===========

.. module:: arrested

Eager to get going? This page gives an introduction to getting started
with Flask-Arrested.

First, make sure that:

* Arrested is :ref:`installed <install>`

This tutorial steps through creating a simple Star Wars themed REST API using Arrested.  We assume you have a working knowledge of both Python and Flask.

Example Application
--------------------

The examples used in this guide can be found here `<https://github.com/mikeywaites/flask-arrested/tree/master/example>`_.

.. note::

    To follow along with the example you will need to install Docker for your operating system.  Find out how here `<https://docker.com>`_.


👋 Alternatively you can use the Arrested cookiecutter to create a working API in 4 simple commands. `<https://github.com/mikeywaites/arrested-cookiecutter>`_.


APIs, Resources and Endpoints - Defining your first API
-------------------------------------------------------------

Flask-Arrested is split into 3 key concepts.  :class:`.ArrestedAPI`'s, :class:`.Resource` and :class:`.Endpoint`.  APIs contian multiple Resources.  For example
Our API contains a Characters resource, a Planets resource and so on.  Resources are a collection of Endpoints.  Endpoints define
the urls inside of our Resources ``/v1/charcaters`` ``/v1/planets/hfyf66775gjgjjf`` etc.

.. code-block:: python

    from flask import Flask

    from arrested import (
        ArrestedAPI, Resource, Endpoint, GetListMixin, CreateMixin,
        GetObjectMixin, PutObjectMixin, DeleteObjectMixin, ResponseHandler
    )

    from example.hanlders import DBRequestHandler, character_serializer
    from example.models import db, Character

    app = Flask(__name__)
    api_v1 = ArrestedAPI(app, url_prefix='/v1')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/code/example/starwars.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    characters_resource = Resource('characters', __name__, url_prefix='/characters')


    class CharactersIndexEndpoint(Endpoint, GetListMixin, CreateMixin):

        name = 'list'
        many = True
        response_handler = DBResponseHandler

        def get_response_handler_params(self, **params):

            params['serializer'] = character_serializer
            return params

        def get_objects(self):

            characters = db.session.query(Character).all()
            return characters

        def save_object(self, obj):

            character = Character(**obj)
            db.session.add(character)
            db.session.commit()
            return character


    class CharacterObjectEndpoint(Endpoint, GetObjectMixin,
                                  PutObjectMixin, DeleteObjectMixin):

        name = 'object'
        url = '/<string:obj_id>'
        response_handler = DBResponseHandler

        def get_response_handler_params(self, **params):

            params['serializer'] = character_serializer
            return params

        def get_object(self):

            obj_id = self.kwargs['obj_id']
            obj = db.session.query(Character).filter(Character.id == obj_id).one_or_none()
            if not obj:
                payload = {
                    "message": "Character object not found.",
                }
                self.return_error(404, payload=payload)

            return obj

        def update_object(self, obj):

            data = self.request.data
            allowed_fields = ['name']

            for key, val in data.items():
                if key in allowed_fields:
                    setattr(obj, key, val)

            db.session.add(obj)
            db.session.commit()

            return obj

        def delete_object(self, obj):

            db.session.delete(obj)
            db.session.commit()


    characters_resource.add_endpoint(CharactersIndexEndpoint)
    characters_resource.add_endpoint(CharacterObjectEndpoint)
    api_v1.register_resource(characters_resource)


Start the Docker container in the example/ directory.

.. code-block:: shell

    $ docker-compose run --rm --service-ports api


Fetch a list of Character objects..

.. code-block:: shell

    curl -X GET localhost:5000/v1/characters | python -m json.tool

	{
		"payload": [
			{
				"created_at": "2017-06-04T11:47:02.017094",
				"id": 1,
				"name": "Obe Wan"
			}
		]
	}

Add a new Character..

.. code-block:: shell

    curl -H "Content-Type: application/json" -d '{"name":"Darth Vader"}' -X POST localhost:5000/v1/characters | python -m json.tool

	{
		"payload": [
			{
				"created_at": "2017-09-01T04:51:45.456072",
				"id": 2,
				"name": "Darth Vader"
			}
		]
	}


Fetch a Character by id..

.. code-block:: shell

    curl -X GET localhost:5000/v1/characters/2 | python -m json.tool

	{
		"payload": {
            "created_at": "2017-09-01T04:51:45.456072",
            "id": 2,
            "name": "Darth Vader"
		}
	}


Update a Character by id..

.. code-block:: shell

    curl -H "Content-Type: application/json" -d '{"id": 2, "name":"Anakin Skywalker", "created_at": "2017-09-01T04:51:45.456072"}' -X PUT localhost:5000/v1/characters/2 | python -m json.tool

	{
		"payload": {
            "created_at": "2017-09-01T04:51:45.456072",
            "id": 2,
            "name": "Anakin Skywalker"
		}
	}


And finally, Delete a Character by id..

.. code-block:: shell

    curl -X DELETE localhost:5000/v1/characters/2


URLS && url_for
^^^^^^^^^^^^^^^^

URLSs are automatically defined by Resoruces and Endpoints using Flask's built in url_mapping functionality.  We optionally provide Resource with a url_prefix which is applied to all of it's registered Endponts.
We can also specify a URI segment for the Endpoint using the ``url`` parameter.  Endpoints require that the name attribute is provied.  This is the name used when reversing the url using Flask's ``url_for`` function.  Ie `url_for('news.list')`
where new is the name given to the Resource and list of the name of one of its registered endpoints.


Getting objects
^^^^^^^^^^^^^^^^

We defined an Endpoint within our characters Resource that accepts incoming GET requests to /v1/characters.  This Endpoint fetches all the Character objects from the database and our custom DBRequestHandler handles converting them
into a format that can be serialized as JSON.  The topic of Request and Response handling is covered in more detail below so for now let's take a closer look at the :class:`.GetListMixin` mixin.

:class:`.GetListMixin` provides automatic handling of GET requests.  It requires that we define a single method :meth:`.GetListMixin.get_objects`.  This method should return data that our specified ResponseHandler can serialize.

We tell Arrested that this endpoint returns many objects using the `many` class attribute.  This setting is used by certain Response handlers when serializing the objects returned by Endpoints.

.. code-block:: python

    import redis
    from arrested import Endpoint, GetListMixin

    class NewsEndpoint(Endpoint, GetListMixin):

        many = True
        name = 'list'

        def get_objects(self, obj):

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news')


Saving objects
^^^^^^^^^^^^^^^^


The CharactersIndexEndpoint also inherits the :class:`.CreateMixin`.  This mixin provides functionality for handling POST requests.  The :class:`.CreateMixin` requires that the :meth:`save_object <CreateMixin.save_object>` method be implemented.
The save_object method will be called with the obj or objects processed by the Endpoint's defined request_handler.


Here's an example Endpoint that store the incoming JSON data in Redis.

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
            r.hmset('news', obj)
            return obj


Object Endpoints
^^^^^^^^^^^^^^^^^

Object endpoints allow you to define APIS that typically let your users GET, PUT, PATCH and DELETE single objects.  The Mixins can be combined to provide support for all the typical HTTP methods used when working with a single object.
Regardless of the HTTP methods you're supporting, your object endpoints must provide the :meth:`get_object <.ObjectMixin.get_object>` method.


Getting a single object
^^^^^^^^^^^^^^^^^^^^^^^^

To support GET requests that retrieve a single object from an Endpoint you should use the :class:`GetObjectMixin <.GetObjectMixin>`.  In addition to the get_object method, we have also specified a url class attribute.  Arrested will populate a kwargs property on your Endpoint instance
which contains the named url paramaters from your Endpoint's url.

Below we use the obj_id passed as part of the url to fetch a new item from Redis by ID.

.. code-block:: python

    import redis
    from arrested import Endpoint, GetObjectMixin

    class CustomEndpoint(Endpoint, GetObjectMixin):

        url = '/<str:obj_id>'
        name = 'object'

        def get_object(self, obj):

            news_id = self.kwargs['obj_id']
            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news:%s' % news_id)


Updating an object
^^^^^^^^^^^^^^^^^^^

Support for updating objects is provided by the :class:`.PutObjectMixin`.  PutObjectMixin requires two methods be implemented. :meth:`get_object <.ObjectMixin.get_object>` and :meth:`update_object <.PutObjectMixin.update_object>`.

.. code-block:: python

    import redis
    from arrested import Endpoint, PutObjectMixin

    class CustomEndpoint(Endpoint, PutObjectMixin):

        url = '/<str:obj_id>'
        name = 'object'

        def get_object(self, obj):

            news_id = self.kwargs['obj_id']
            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news:%s' % news_id)

        def update_object(self, obj):

            news_id = self.kwargs['obj_id']
            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmset('news:%s' % news_id, obj)

When a PUT request is handled by our CustomEndpoint the :meth:`get_object <.ObjectMixin.get_object>` method is called first to retrieve the existing object.  If an object is found
the :meth:`.PutObjectMixin.update_object` method is then called.

To support updating objects via PATCH requests all we need to do is use the :class:`.PatchObjectMixin`.  It works in same way as :class:`.PutObjectMixin`
except that we the :meth:`patch_object <.PatchObjectMixin.patch_object>` method is called when an object is returned by get_object.


.. code-block:: python

    import redis
    from arrested import Endpoint, PutObjectMixin, PatchObjectMixin

    class CustomEndpoint(Endpoint, PutObjectMixin, PatchObjectMixin):

        url = '/<str:obj_id>'
        name = 'object'

        def get_object(self, obj):

            news_id = self.kwargs['obj_id']
            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news:%s' % news_id)

        def do_update(self, obj):

            news_id = self.kwargs['obj_id']
            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmset('news%s' % news_id, obj)

        def update_object(self, obj):

            self.do_update(obj)

        def patch_object(self, obj):

            self.do_update(obj)


Deleting objects
^^^^^^^^^^^^^^^^^

Support for deleting objects is provided by the :class:`.DeleteObjectMixin`.  DeleteObjectMixin requires two methods be implemented. :meth:`get_object <.ObjectMixin.get_object>` and :meth:`delete_object <.DleteObjectMixin.delete_object>`.

.. code-block:: python

    import redis
    from arrested import Endpoint, DeleteObjectMixin

    class CustomEndpoint(Endpoint, DeleteObjectMixin):

        url = '/<str:obj_id>'
        name = 'object'

        def get_object(self, obj):

            news_id = self.kwargs['obj_id']
            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            return r.hmget('news:%s' % news_id)

        def delete_object(self, obj):

            news_id = self.kwargs['obj_id']
            return r.delete('news:%s' % news_id)


Middleware
-------------------

Flask comes with a great system for defining request middleware.  Arrested builds on top of this system to allow more fine grained control of where and when your middleware is run.

API Middleware
^^^^^^^^^^^^^^^^^

Middleware can be applied at each level of the Arrested stack.  You will often want a piece middleware to be applied across every resource and every endpoint defined in an API.  An example of this might be authentication.
The :class:`.ArrestedAPI` object supports two middleware hooks, ``before_all_hooks`` and ``after_all_hooks``. Let's create a basic example that demonstrates how authentication can be applied across APIs.


.. code-block:: python

    def authenticated(endpoint):
        token_valid = request.args.get('token') == 'test-token'
        if not token_valid:
            endpoint.return_error(401)

    api_v1 = ArrestedAPI(app, url_prefix='/v1', before_all_hooks=[authenticated])


Hit the ``http://localhost:5000/v1/characters`` url in your browser. We now get a 401 status code when requesting the characters API.
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
from every after request hook defined on our APIs and Resources.

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

As you can see, not only can we dfine the before_all_hooks and after_all_hooks like we have on the :class:`.ArrestedAPI` and :class:`.Resource`, we can also inject middleware before and after each HTTP method.
Let's update our CharacterObjectEndpoint to require an admin for PUT requests.

.. code-block:: python

    def is_admin(endpoint):

        endpoint.return_error(403)

    class CharacterObjectEndpoint(Endpoint, GetObjectMixin,
                                  PutObjectMixin, DeleteObjectMixin):

        name = 'object'
        url = '/<string:obj_id>'
        response_handler = DBResponseHandler
        before_put_hooks = [is_admin, ]

        def get_response_handler_params(self, **params):

            params['serializer'] = character_serializer
            return params

        def get_object(self):

            obj_id = self.kwargs['obj_id']
            obj = db.session.query(Character).filter(Character.id == obj_id).one_or_none()
            if not obj:
                payload = {
                    "message": "Character object not found.",
                }
                self.return_error(404, payload=payload)

            return obj

        def update_object(self, obj):

            data = self.request.data
            allowed_fields = ['name']

            for key, val in data.items():
                if key in allowed_fields:
                    setattr(obj, key, val)

            db.session.add(obj)
            db.session.commit()

            return obj

        def delete_object(self, obj):

            db.session.delete(obj)
            db.session.commit()


Making a PUT request to ``http://localhost:5000/v1/characters/1`` using curl now returns a 403


Handling Requests and Responses
--------------------------------

Arrested provides a flexible API for handling the data flowing into, and out from your APIs.  Each endpoint can have a custom :class:`.RequestHandler` and :class:`ResponseHandler`.  This system provides support for any concievable way of processing data.  Arrested also provides some out of the box integrations with popular
serialization libraries, such as Kim and Marshmallow.

Request Handling
^^^^^^^^^^^^^^^^^

HTTP requests that process data require that a :class:`.RequestHandler` is defined on the Endpoint using the request_handler property.  The default :class:`.RequestHandler` simply pulls the json data from the Flask request object, deserialises it into a dict and returns it verbatim.
Let's suppose we want to apply some **very** basic validation ensuring that certain keys are present within the request payload.  To do this we will implement a custom :class:`.RequestHandler` that takes a list of field names and ensures all the keys are present in the request data.


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


This simple examples demonstrates the flexibility the handler system offers.  We can define handlers to accomodate any use case imaginable in Python.  We can use the :meth:`.Endpoint.get_request_handler_params` to configure the handler
on an endpoint by endpoint basis.

Accessing the Request object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We've seen how to define a custom handler and how we configure it to process incoming data.  So what does arrested do with all this stuff?  Whenever a POST, PUT, PATCH request is made to one of your :class:`.Endpoint` arrested will instantiate the ``request`` object and set it on the Endpoint.
This allows users to access the handler instance used to process the incoming request.  An example of this in practice is the :meth:`CreateMixin.handle_post_request` method.

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
This works fine in simple cases but when we're dealing with more complex types like SQLAlchemy Models we need something a bit smarter.

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

As we saw with the Request object, Arrested will store the response handler instance against a property on the Endpoint called ``response``.  By default a ResponseHandler is created for any request handled by an Endpoint.
This means that the data generated by a RequestHandler will later be processed and returned by the provided ResponseHandler.  We can see this in action in the :class:`.PutObjectMixin` mixin shown below.

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


Handling Errors
^^^^^^^^^^^^^^^^^

Returning specific HTTP status codes under certain conditions is an important part of building REST APIs.  Arrested provides users with a simple, and consistent way to handle generating error responses
from their Endpoints.  An example of this might be returning a 404 when an object is not found.

Our CharacterObjectEndpoint has already demonstrated this above in the get_object method.  When we fail to find the object we're looking for from the database, we call the :meth:`.Endpoint.return_error` method
to have Flask abort execution of the request and immediately return an error.

We simply provide the status code we want to return along with an optional request payload that will be serialized as JSON and retured as the response body.


.. code-block:: python

    def get_object(self):

        obj_id = self.kwargs['obj_id']
        obj = db.session.query(Character).filter(Character.id == obj_id).one_or_none()
        if not obj:
            payload = {
                "message": "Character object not found.",
            }
            self.return_error(404, payload=payload)

        return obj
