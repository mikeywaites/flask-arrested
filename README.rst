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

Introducing Arrested
---------------------

Take the pain out of REST API creation with Arrested - batteries included for quick wins, highly extensible for specialist requirements.

.. code-block:: python

    from arrested import ArrestedAPI, Resource, Endpoint, GetListMixin, CreateMixin,
    from example.models import db, Character

    api_v1 = ArrestedAPI(url_prefix='/v1')

    characters_resource = Resource('characters', __name__, url_prefix='/characters')


    class CharactersIndexEndpoint(Endpoint, GetListMixin, CreateMixin):

        name = 'list'
        many = True

        def get_objects(self):

            characters = db.session.query(Character).all()
            return characters

        def save_object(self, obj):

            character = Character(**obj)
            db.session.add(character)
            db.session.commit()
            return character


    characters_resource.add_endpoint(CharactersIndexEndpoint)
    api_v1.register_resource(characters_resource)


Flask-Arrested Features
-----------------------------

Arrested is a framework for rapidly building REST API's with Flask.

- Un-Opinionated: Let's you decide "the best way" to implement *your* REST API.
- Battle Tested: In use across many services in a production environment.
- Batteries Included! Arrested ships with built in support for popular libraries such as SQLAlchemy, Kim and Marshmallow.  Using something different or have your own tooling you need to support?  Arrested provides a rich API that can be easily customised!
- Supports any storage backends:  Want to use "hot new database technology X?" No problem!  Arrested can be easily extended to handle all your data needs.
- Powerful middleware system - Inject logic at any step of the request/response cycle


🚀 Get started in under a minute..
-----------------------------------------

.. raw:: html

    <script type="text/javascript" src="https://asciinema.org/a/UbBr97GeGlLNMTT64HNvjF3Ql.js" id="asciicast-UbBr97GeGlLNMTT64HNvjF3Ql" async data-autoplay="true" data-size="small" data-rows=20></script>

Use the Flask-Arrested cookie cutter to create a basic API to get you started in 4 simple commands. `<https://github.com/mikeywaites/arrested-cookiecutter>`_.


.. code-block:: shell

    $ cookiecutter gh:mikeywaites/arrested-cookiecutter
    $ cd arrested-users-api
    $ docker-compose up -d api
    $ curl -u admin:secret localhost:8080/v1/users | python -m json.tool

----------------

The User Guide
--------------

Get started with Flask-Arrested using the quickstart user guide or take a look at the in-depth API documentation.

`<https://arrested.readthedocs.org>`_.
