.. _kim:

Kim
=============

Kim is a Serialization and Marshaling framework.  Arrested provides out of the box integration with Kim, providing you with the ability to serialize and deserialize complex object types.

You can read more about Kim at `Read the docs <http://kim.rtfd.org>`_. or check out the source code on `GitHub <https://github.com/mikeywaites/kim>`_.

Let's refactor the Characters resource from the quickstart example application to integrate with Kim.

Usage
---------

.. code-block:: python

    from arrested.contrib.kim_arrested import KimEndpoint
    from kim import Mapper, field, role


    class CharacterMapper(Mapper):
        __type__ = Character

        id = field.Integer(read_only=True)
        name = field.String()
        created_at = field.Datetime(read_only=True)


    class CharactersIndexEndpoint(KimEndpoint, GetListMixin, CreateMixin):

        name = 'list'
        many = True
        mapper_class = CharacterMapper

        def get_objects(self):

            characters = db.session.query(Character).all()
            return characters

        def save_object(self, obj):

            db.session.add(obj)
            db.session.commit()
            return obj


    class CharacterObjectEndpoint(KimEndpoint, GetObjectMixin,
                                  PutObjectMixin, DeleteObjectMixin):

        name = 'object'
        url = '/<string:obj_id>'
        mapper_class = CharacterMapper

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


So what's changed?  Firstly we are now using the :class:`KimEndpoint <arrested.contrib.kim_arrested.KimEndpoint>` class when defining our Endpoints.  This Custom base Endpoint does the grunt work for us.
It defines the custome Kim Response and Request handlers and the get_response_handler_params and get_request_handler_params methods to set them up.

This has had some impact on our CharactersIndexEndpoint and CharacterObjectEndpoint too.  We no longer need to manually instantiate the Character model ourselves and we've thankfully removed that really basic validation from the update_object method.  Kim now provides robust validation of the data coming into our API ensuring data is present and of the correct type.
