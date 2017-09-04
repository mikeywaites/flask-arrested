.. Flask-Arrested documentation master file, created by
   sphinx-quickstart on Sun Feb 26 15:02:48 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flask-Arrested: A Framework For Rapidly Building REST APIs with Flask.
=======================================================================

Release v\ |version|. (:ref:`Installation <install>`)

-------------------

**Introducing Arrested**::

    from flask import Flask
    from arrested import ArrestedAPI
    from arrested.endpoints import Endpoint
    from arrested.contrib.sql_alchemy import DBCreateMixinx, DBListMixin
    from arrested.contrib.kim_arrested import KimRequestHandler, KimResponseHandler

    from .mappers import UserMapper

    app = Flask(__name__)
    api_v1 = ArrestedAPI(app)

    class UsersEndpoint(Endpoint, DBCreateMixin, DBListMixin):

        url = '/users'
        endpoint_name = 'users.index'
        response_handler = KimResponseHandler
        request_handler = KimRequestHandler

        def get_handler_params(self):
            return {
                'mapper': UserMapper
            }

        def get_query(self):

            return User.get_users()

        def save_object(self, obj):

            db.session.add(obj)
            db.session.flush()

    api_v1.register(UsersEndpoint)



Flask-Arrested Features
-----------------------------

Arrested is a framework for rapidly building REST API's with Flask.

- Un-Opinionated: Let's you decide "the best way" to implement *your* REST API.
- Battle Tested: In use across many services in a production environment.
- Bring your own tools! Easily customisable Request and Response handling with your tools of choice.
- Support all storage backends:  Wanna use "hot new database technology X?" No problem!  Arrested lets you easily extend to handle all your data needs.

Arrested officially supports Python 2.7 & 3.3–3.5

The User Guide
--------------

Get started with Flask-Arrested using the quickstart user guide or take a look at the in-depth advanced documentation.

.. toctree::
   :maxdepth: 2

   guide/intro
   guide/install
   guide/quickstart

.. toctree::
   :maxdepth: 3

   guide/advanced


The API Documentation / Guide
-----------------------------

Detailed class and method documentation

.. toctree::
   :maxdepth: 3

   api
