from flask import current_app as app
from ..mixins import (
    GetListMixin, CreateMixin, GetObjectMixin,
    PutObjectMixin, PatchObjectMixin,
    DeleteObjectMixin
)


class DBMixin(object):

    def get_query(self):
        """Return an SQLAlchemy Query object.  Users using this mixin should  override
        this method.

        The Mixins that call this method expect a Query method to be returned so
        that they can apply additional filtering automatically.
        Things like pagination middleware also require a Query object.

        Useage::

            class MyEndpoint(Endpoint, DBObjectMixin):

                def get_query(self):
                    return db.session.query(User).filter(
                        User.is_active == true()
                    )

        In the example above, Arrested will automatically apply a primary key filter to
        the query returned by :meth:`DBMixin.get_query`.

        :returns: SQLAlchemy Query object
        :raises: NotImplementedError

        .. seealso::

            :meth:`DBObjectMixin.get_objects`
            :meth:`DBListMixin.get_result`
            :meth:`DBObjectMixin.get_object`
            :meth:`DBObjectMixin.get_result`
        """
        raise NotImplementedError('DBListMixin must implement the get_query method.')

    def get_db_session(self):
        """
        """
        return app.extensions['sqlalchemy'].db.session


class DBListMixin(GetListMixin, DBMixin):
    """SQLAlchemy powered list mixin that queries a database to retun a list of results
    for a given endpoint.

    Usage::

        from arrested import Resource, Endpoint
        from arrested.contrib.sqa import DBListMixin
        from arrested.contrib.kim import KimRequestHandler, KimResponseHandler

        from .models import db, Character

        characters_resource = Resource('characters', __name__, url_prefix='/characters')

        class CharactersEndpoint(Endpoint, DBListMixin):

            name = 'list'
            response_handler = KimResponseHandler
            request_handler = KimRequestHandler

            def get_query(self):

                return db.session.query(Character).order_by(
                    Character.created_at.desc()
                ).all()

        characters_resource.add_endpoint(CharactersEndpoint)

    """

    def get_result(self, query):
        """Cast the query into a scalar python type.

        :param query: SQLAlchemy Query
        :returns: A list of objects returned by the Query or an empty list
        """

        return query.all()

    def get_objects(self):
        """Implements the GetListMixin interface and calls :meth:`DBListMixin.get_query`.
        Using this mixin requires usage of a response handler capable of serializing
        SQLAlchemy query result objects.

        :returns: Typically a SQLALchemy Query result.
        :rtype: mixed

        .. seealso::
            :meth:`DBListMixin.get_query`
            :meth:`DBListMixin.get_result`
        """

        return self.get_result(self.get_query())


class DBCreateMixin(CreateMixin, DBMixin):

    def save_object(self, obj):
        """Takes a marshalled object and attempts to save it to the database using
        a SQlAlchemy session.
        """
        session = self.get_db_session()
        session.add(obj)
        session.commit()


class DBObjectMixin(GetObjectMixin, DBMixin):
    """SQLAlchemy powered object mixin that queries a database to retun a single object
    typically by primary key for a given endpoint.

    Usage::

        from arrested import Resource, Endpoint
        from arrested.contrib.sqa import DBObjectMixin
        from arrested.contrib.kim import KimRequestHandler, KimResponseHandler

        from .models import db, Character

        characters_resource = Resource('characters', __name__, url_prefix='/characters')

        class CharacterObjectEndpoint(Endpoint, DBObjectMixin):

            url = '/<integer:obj_id>'
            name = 'object'
            response_handler = KimResponseHandler
            request_handler = KimRequestHandler

            def get_query(self):

                return db.session.query(Character).filter()

        characters_resource.add_endpoint(CharacterObjectEndpoint)
    """

    url_id_param = 'obj_id'
    model_id_param = 'id'

    def get_result(self, query):
        """Cast the query into a scalar python type.

        :param query: SQLAlchemy Query
        :returns: An object returned by the Query or None
        """
        return query.one_or_none()

    def filter_by_id(self, query):
        """Apply the primary key filter to query to filter the results for a specific
        instance by id.

        The filter applied by the this method by default can be controlled using the
        url_id_param

        :param query: SQLAlchemy Query
        :returns: A SQLAlchemy Query object
        """

        return query.filter_by(**{self.model_id_param: self.kwargs[self.url_id_param]})

    def get_object(self):
        """Implements the GetObjectMixin interface and calls
        :meth:`DBObjectMixin.get_query`.  Using this mixin requires usage of
        a response handler capable of serializing SQLAlchemy query result objects.

        :returns: Typically a SQLALchemy Query result.
        :rtype: mixed

        .. seealso::
            :meth:`DBObjectMixin.get_query`
            :meth:`DBObjectMixin.filter_by_id`
            :meth:`DBObjectMixin.get_result`
        """
        query = self.get_query()
        query = self.filter_by_id(query)
        return self.get_result(query)


class DBUpdateMixin(PutObjectMixin, PatchObjectMixin, DBMixin):
    pass


class DBDeleteMixin(DeleteObjectMixin, DBMixin):
    pass
