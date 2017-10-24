.. _sqlalchemy:

Flask-SQLAlchemy
=================

Arrested comes with built in support for working with Flask-SQLAlchemy. The SQLAlchemy mixins support automatically committing the database session when saving objects,
filtering Queries by a model's primary key when fetching single objects and the removal of objects from the database when deleting. Simply put, the SQLAlchemy mixin takes
care of the boring stuff when integrating Arrested with SQLAlchemy.

.. note::

    The referrence to Flask-SQLAlchemy does not strictly mean you can't use vanilla SQLAlchemy with Arrested.  See the section on providing access to the SQLAlchemy session object below for more information on custom configurations.


Usage
---------

Let's refactor the Characters resource from the quickstart example application to integrate with Flask-SQLAlchemy.

.. code-block:: python

    from arrested.contrib.sql_alchemy import DBListMixin, DBCreateMixin, DBObjectMixin

    class CharacterMixin(object):

        response_handler = DBResponseHandler
        model = Character

        def get_query(self):

            stmt = db.session.query(Character)
            return stmt

    class CharactersIndexEndpoint(Endpoint, DBListMixin, DBCreateMixin, CharacterMixin):

        name = 'list'
        many = True

        def get_response_handler_params(self, **params):

            params['serializer'] = character_serializer
            return params


    class CharacterObjectEndpoint(Endpoint, DBObjectMixin, CharacterMixin):

        name = 'object'
        url = '/<string:obj_id>'

        def get_response_handler_params(self, **params):

            params['serializer'] = character_serializer
            return params

        def update_object(self, obj):

            data = self.request.data
            allowed_fields = ['name']

            for key, val in data.items():
                if key in allowed_fields:
                    setattr(obj, key, val)

            return super(CharacterObjectEndpoint, self).update_object(obj)

We've managed to remove quite a bit of boilerplate code by using the DBMixins provided by the SQLAlchemy contrib module.  We no longer need to add the objects to the session ourselves when creating or updating objects.  We also removed the code from get_object that would return a 404 if the object was not found as the DBObjectMixin, by default, does this for us.
Lastly, we removed the delete_object method as the DBObjectMixin takes care of this by default.


DBListMixin
~~~~~~~~~~~~~~~~~~~

The :class:`DBListMixin <arrested.contrib.sql_alchemy.DBListMixin>` mixin implments the standard :class:`.GetListMixin` interface.  We'd normally be required to implement the :meth:`.GetListMixin.get_objects` method.  DBListMixin handles this method and instead requires the :meth:`get_query <arrested.contrib.sql_alchemy.DBListMixin.get_query>` method.
This method should return a Query object as opposed to a scalar Python type.  DBListMixin will automatically call ``.all()`` on the Query object for you.  If for some reason you need to handle this yourself you can overwrite the :meth:`get_result <arrested.contrib.sql_alchemy.DBListMixin.get_result>` method.


.. code-block:: python

    def get_query(self):

        return db.session.query(Character).all()

    def get_result(self, query):

        if isinstance(query, list):
            return query
        else:
            return query.all()


DBObjectMixin
~~~~~~~~~~~~~~~~~~~~~

The :class:`DBListMixin <arrested.contrib.sql_alchemy.DBObjectMixin>` mixin implements the :class:`.ObjectMixin` interface.  It provides handling for GET, PATCH, PUT and DELETE requests for single objects in a single mixin.  When implementing the DBObjectMixin interace we'd normally be required to implement the :meth:`get_object <.ObjectMixin.get_object>` method.  Instead the DBObjectMixin requires the :meth:`get_query <arrested.contrib.sql_alchemy.DBObjectMixin>` method.
This method should return a Query object opposed to a scalar Python type.  DBObjectMixin will automatically apply a WHERE clause to filter the returned Query object by the primary key of the Endpoints model.

Filtering queries by id
^^^^^^^^^^^^^^^^^^^^^^^^

The automatic filtering of the returned Query object can be configured using some class level attributes exposed by the DBObjectMixin class.

.. code-block:: python

    class CharacterObjectEndpoint(Endpoint, DBObjectMixin, CharacterMixin):

        name = 'object'
        url = '/<string:slug>'
        url_id_param = 'slug'
        model_id_param = 'slug'

        def get_response_handler_params(self, **params):

            params['serializer'] = character_serializer
            return params

        def update_object(self, obj):

            data = self.request.data
            allowed_fields = ['name']

            for key, val in data.items():
                if key in allowed_fields:
                    setattr(obj, key, val)

            return super(CharacterObjectEndpoint, self).update_object(obj)

The ``model_id_param`` and ``url_id_param`` are used in conjunction to pull a custom kwarg from our url_mapping rule and then use it to filter a "slug" field on our model.


Cutom result handling
^^^^^^^^^^^^^^^^^^^^^^

We can also control how DBObjectMixin converts the Query obejct returned by get_query into a scalar Python type using the :meth:`get_result <arrested.contrib.sql_alchemy.DBObjectMixin.get_result>`.  By default, DBObjectMixin will call ``one_or_none()`` on the Query object
returned.


.. code-block:: python

    def get_result(self, query):

        # We've already handled the query, just return it..
        return query


Custom Session configuration
-----------------------------

Arrested assumes that you're using SQLAlchemy with Flask.  You can configure the DBMixins to work with other flavours of SQLAlchemy setup's.  By default Arrested will attempt to pull the SQLAlchemy db session from
you Flask app's configured extensions.  The :meth:`get_db_session <arrested.contrib.sql_alchemy.DBMixin.get_db_session>` method simply needs to return a valid SQLAlchemy session object.

.. code-block:: python

    def get_db_session(self):
        """Returns the session configured against the Flask appliction instance.
        """
        return my_session
