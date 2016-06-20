Defining API Endpoints
========================

Arrested provides everything you need to define your RESTFul api in flask.  It
comes with several built in classes for implmenting common rest paradigms as well as a flexible api
for implemening custom logic where requried.


Request and Response handlers
-----------------------------

A key concept of Arrested is that it makes no assumptions about the way you marhsal and serialize your data.
It provides a simple interface for processing requests (Marshaling) and responses (Serialization) with the use of
:py:class:`RequestHandler` and :py:class:`ResponseHandler` classes which are defined on your resources.

This allows users to use their own flavour of data handling.  It might be a framework like Marshmallow or Kim or even your own
vanilla serializers.

.. codeblock:: python


    class MyRequestHandler(RequestHandler):

        def get_objects(self, data):

            return covert_from_json(data)


    class UsersIndexApi(IndexApi):

        methods = ['POST']
        urls = '/users'
        endpoint_name = 'users.index'
        request_handler = KimRequestHandler


.. seealso:
    :py:class:`Handler`



Request Hooks
----------------

Arrested Provides a system for defining hooks that are run on a per request, per api basis.  Under the hood that resolve to
flask before_request and after_hooks wrapped in some logic to selectively apply the hook given that the URL and HTTP method are valid.

.. codeblock:: python

    class UsersIndexApi(Api, ListableResource, CreateableResource):

        methods = ['GET']
        urls = '/users'
        endpoint_name = 'users.index'
        response_handler = KimResponseHandler
        request_handler = KimRequestHandler

        @hook(methods=['GET'], type_='before_request')
        def log_request(self):

            logger.debug('request made')

        @hook(methods=['POST'], type_='after_request')
        def send_email(self, request):

            send_email()

            return request


Allowed HTTP Methods
-----------------------

Its often the case that you have a resource located somewhere like `/v1/users` but you only want to permit
'GET' requests to this api.  The allowed HTTP methods can be controlled using the methods class atrribute on your
Resources.

.. codeblock:: python

    class UsersIndexApi(IndexApi):

        methods = ['GET']
        urls = '/users'
        endpoint_name = 'users.index'
        response_handler = KimResponseHandler
        request_handler = KimRequestHandler


Having only specified 'GET' in the mehods attribute, this api will now only accept GET requests and return a 405 Method Not Allowed
HTTP response for anything else.


Index Apis
~~~~~~~~~~~~

IndexApis are responsible for handling GET and POST requests to the route of one of your resources.
Imagine we have a table of users stored in our database and we want to expose these user to our api clients.
We would typically structure the urls along the lines of `https://api.example.com/v1/users` and then for a single user
object we would provide a resource located at `https://api.example.com/v1/users/:id`.


To achieve this functionality all we'd need to do is define a new :py:class:`IndexApi`.

.. codeblock:: python

    from flask import Flask
    from arrested import Api
    from arrested.handlers import KimResponseHandler, KimRequestHandler

    app = Flask(__name__)
    api = Api(app)

    class UsersIndexApi(IndexApi):

        urls = '/users'
        endpoint_name = 'users.index'
        response_handler = KimResponseHandler
        request_handler = KimRequestHandler

        def get_objects(self):

            return get_users()

        def save_object(self, obj):

            db.session.add(obj)
            db.session.commit()

    api.register(UsersIndexApi)


When handling GET requests IndexApi requires that the user implement the get_objects method.
This method should return a list of objects that can be serialized by the ResponseHandler you have
specified.

List Mixins
------------------

Arrested Provides some mixins that encapulate common approaches to handling requests to create and return collections of
objects.

The ModelListMixin provides an api to simply implement a get_query() method that will return results using an ORM like SQlAlchemy.
see (Mixins) for more information on the options available.
