# Arrested: A Framework for rapidly building REST APIs with Flask

Release v\ |version|. (:ref:`Installation <install>`)

-------------------

**Introducing Arrested**::

    from flask import Flask
    from arrested import ArrestedAPI, Endpoint, Resource
    from arrested.contrib.sql_alchemy import DBCreateMixinx, DBListMixin
    from arrested.contrib.kim_arrrested import KimRequestHandler, KimResponseHandler
    from arrested.contrib.oauth import OAuthMixin

    from .mappers import UserMapper

    app = Flask(__name__)
    api_v1 = ArrestedAPI(app)

    users_resource = Resource('users')

    class BaseEndpoint(Endpoint, OAuthMixin):
        response_handler = KimResponseHandler
        request_handler = KimRequestHandler

    class IndexAPI(BaseEndpoint, DBListMixin, DBCreateMixin):

        scopes = ['read']

	class UsersEndpoint(IndexAPI):

        response_handler = KimResponseHandler
        request_handler = KimRequestHandler
        mapper = UserMapper

        def get_query(self):

            return User.get_users()

        def save_object(self, obj):

            db.session.add(obj)
            db.session.flush()

    users_resource.add(UsersEndpoint, url='users')
    ap1_v1.reigster(users_resource)



## Flask-Arrested Features
-----------------------------

Arrested is a framework for rapidly building REST API's with Flask.

- Un-Opinionated: Let's you decide "the best way" to implement *your* REST API.
- Battle Tested: In use across many services in a production environment.
- Bring your own tools! Easily customisable Request and Response handling with your tools of choice.
- Support all storage backends:  Wanna use "hot new database technology X?" No problem!  Arrested lets you easily extend to handle all your data needs.

Arrested officially supports Python 2.7 & 3.3–3.5
