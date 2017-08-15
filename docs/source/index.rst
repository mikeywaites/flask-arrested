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
    from arrested import ArrestedAPI, Resource
    from arrested.contrib.kim import KimEndpoint
    from arrested.contrib.sqla import DBCreateMixinx, DBListMixin
    from arrested.contrib.sql_alchemy import DBCreateMixinx, DBListMixin
    from arrested.contrib.kim_arrested import KimRequestHandler, KimResponseHandler

    from .models import Character

    from kim import Mapper, field


    class CharacterMapper(Mapper):

        __type__ = Character

        id = field.Integer(read_only=True)
        name = field.String()
        created_at = field.DateTime(read_only=True)

    app = Flask(__name__)
    api_v1 = ArrestedAPI(app, url_prefix='/v1)

    characters_resource = Resource('characters', __name__, url_prefix='/characters')

    class CharactersListEndpoint(KimEndpoint, DBListMixin, DBCreateMixin):

        name = 'list'
        many = True
        mapper_class = CharacterMapper

        def get_query(self):

            return db.session.query(Character)


    class CharacterObjectEndpoint(KimEndpoint, DBObjectMixin):

        name = 'object'
        url = '/<string:obj_id>'
        mapper_class = CharacterMapper

        def get_query(self):

            return db.session.query(Character)




Flask-Arrested Features
-----------------------------

Arrested is a framework for rapidly building REST API's with Flask.

- Un-Opinionated: Let's you decide "the best way" to implement *your* REST API.
- Battle Tested: In use across many services in a production environment.
- Batteries Included! Arrested ships with built in support for popular libraries such as SQLAlchemy, Kim and Marshmallow.  Using something different or have your own tooling your need to support?  Arrested provides a rich API that can be easily customised!
- Supports any storage backends:  Want to use "hot new database technology X?" No problem!  Arrested can be easily extended to handle all your data needs.
- Powerful middleware system - Inject logic at any step of the request/response cycle

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
