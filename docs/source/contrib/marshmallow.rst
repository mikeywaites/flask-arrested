.. _marshmallow:

Marshmallow
=============

Marshmallow is a Serialization and Marshaling framework.  Arrested provides out of the box integration with Marshmallow, providing you with the ability to serialize and deserialize complex object types.

You can read more about Marshmallow at `Read the docs <http://http://marshmallow.readthedocs.io/>`_. or check out the source code on `GitHub <https://github.com/marshmallow-code/marshmallow>`_.

Let's refactor the Characters resource from the quickstart example application to integrate with Marshmallow.

Usage
---------

.. code-block:: python

    from arrested.contrib.marshmallow_arrested import Marshmallow
    from marshmallow import Schema, fields


    class CharacterSchema(Schema):
        __type__ = Character

        id = fields.Integer(read_only=True)
        name = fields.Str(required=True)
        created_at = field.Datetime(read_only=True)


    class CharactersIndexEndpoint(MarshamallowEndpoint, GetListMixin, CreateMixin):

        name = 'list'
        many = True
        schema_class = CharacterSchema

        def get_objects(self):

            characters = db.session.query(Character).all()
            return characters

        def save_object(self, obj):

            db.session.add(obj)
            db.session.commit()
            return obj


    class CharacterObjectEndpoint(MarshmallowEndpoint, GetObjectMixin,
                                  PutObjectMixin, DeleteObjectMixin):

        name = 'object'
        url = '/<string:obj_id>'
        schema_class = CharacterSchema

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

            db.session.add(obj)
            db.session.commit()

            return obj

        def delete_object(self, obj):

            db.session.delete(obj)
            db.session.commit()


So what's changed?  Firstly we are now using the :class:`MarshmallowEndpoint <arrested.contrib.marshmallow_arrested.MarshmallowEndpoint>` class when defining our Endpoints.  This Custom base Endpoint does the grunt work for us.
It defines the custom Marshmallow Response and Request handlers and the get_response_handler_params and get_request_handler_params methods to set them up.

This has had some impact on our CharactersIndexEndpoint and CharacterObjectEndpoint too.  We no longer need to manually instantiate the Character model ourselves and we've thankfully removed that really basic validation from the update_object method.  Marshmallow now provides robust validation of the data coming into our API ensuring data is present and of the correct type.
