Quickstart
=============

Here's a very basic working example of using Flask-Arrested to define an
SQLAlchemy back User rest api.  The Example uses the Kim - JSON Marhsaling and Serialization framework
to process both incoming and outgoing data.

.. codeblock:: python

    from flask import Flask
    from arrested import Api
    from arrested.mixins import ModeListMixin
    from arrested.handlers import KimResponseHandler, KimRequestHandler

    app = Flask(__name__)
    api = Api(app)

    class UsersIndexApi(IndexApi, ModelListMixin):

        urls = '/users'
        endpoint_name = 'users.index'
        response_handler = KimResponseHandler
        request_handler = KimRequestHandler

        def get_query(self):

            return get_users()


    api.register(UsersIndexApi)
