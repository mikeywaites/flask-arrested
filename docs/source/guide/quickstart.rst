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


Defining your first API
-------------------------

Flask-Arrested is split into 3 key concepts.  API's, Resources and Endpoints.  API's contian multiple Resources.  For example
Our API will contain a Characters resource, a Planets resource and so on.  Resources are a collection of Endpoints.  Endpoints define
the urls inside of our Resources ``/v1/charcaters`` ``/v1/planets/hfyf66775gjgjjf`` etc.

Our API will...

* Return a list of all the characters from the DB from the /v1/characters url
* Return a specifc character from the DB by id from the url /v1/characters/:id
* Allow users to create a new character when by a POST request to /v1/characters
* Allow users to update a character by making a PUT request to /v1/characters/:id
* And finally, allow users to delete a character by making a DELETE request to /v1/characters/:id

.. note::

    To follow along with the example you will need to install Docker for your operating system.  Find out how here.

.. code-block:: python

    from flask import Flask

    from arrested import ArrestedAPI, Resource
    from arrested.contrib.sqa import (
        DBListMixin,
        DBCreateMixin,
        DBObjectMixin,
        DBUpdateMixin
    )
    from arrested.contrib.kim import KimEndpoint

    from example.models import db, Character
    from example.mappers import CharacterMapper


    app = Flask(__name__)
    api_v1 = ArrestedAPI(app, url_prefix='/v1')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/code/example/starwars.db'
    db.init_app(app)

    characters_resource = Resource('characters', __name__, url_prefix='/characters')

    class CharactersEndpoint(KimEndpoint, DBListMixin, DBCreateMixin):

        name = 'list'
        many = True
        mapper_class = CharacterMapper

        def get_query(self):

            return db.session.query(Character)


    class CharacterObjectEndpoint(KimEndpoint, DBObjectMixin, DBUpdateMixin):

        name = 'object'
        mapper_class = CharacterMapper

        def get_query(self):

            return db.session.query(Character)

    characters_resource.add_endpoint(CharactersEndpoint)
    characters_resource.add_endpoint(CharacterObjectEndpoint)
    api_v1.register_resource(characters_resource)


Start the Docker container in the example/ directory.

.. code-block:: shell

    $ docker-compose run --rm --service-ports api

Hit the `http://localhost:5000/v1/characters` url in your browser.  You will see the JSON response
for the characters endpoint returned.
