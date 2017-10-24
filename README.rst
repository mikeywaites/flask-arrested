Flask-Arrested: A Framework For Rapidly Building REST APIs with Flask.
=======================================================================

.. image:: https://img.shields.io/pypi/v/arrested.svg
    :target: https://pypi.python.org/pypi/arrested

.. image:: https://img.shields.io/pypi/l/arrested.svg
    :target: https://pypi.python.org/pypi/arrested

.. image:: https://img.shields.io/pypi/pyversions/arrested.svg
    :target: https://pypi.python.org/pypi/arrested

.. image:: https://circleci.com/gh/mikeywaites/flask-arrested/tree/master.svg?style=svg
    :target: https://circleci.com/gh/mikeywaites/flask-arrested/tree/master

.. image:: https://img.shields.io/readthedocs/arrested/latest.svg
    :target: http://arrested.readthedocs.io/en/latest/

.. image:: https://coveralls.io/repos/github/mikeywaites/flask-arrested/badge.svg?branch=master
    :target: https://coveralls.io/github/mikeywaites/flask-arrested?branch=master

.. image:: https://badges.gitter.im/bruv-io/Arrested.png
    :target: https://gitter.im/bruv-io/Arrested

-------------------

Flask-Arrested Features
-----------------------------

Arrested is a framework for rapidly building REST API's with Flask.

- Un-Opinionated: Let's you decide "the best way" to implement *your* REST API.
- Battle Tested: In use across many services in a production environment.
- Batteries Included! Arrested ships with built in support for popular libraries such as SQLAlchemy, Kim and Marshmallow.  Using something different or have your own tooling you need to support?  Arrested provides a rich API that can be easily customised!
- Supports any storage backends:  Want to use "hot new database technology X?" No problem!  Arrested can be easily extended to handle all your data needs.
- Powerful middleware system - Inject logic at any step of the request/response cycle


Pip Install Flask-Arrested
---------------------------

To install Arrested, simply run this command in your terminal of choice::

$ pip install arrested


Introducing Arrested
-----------------------

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
