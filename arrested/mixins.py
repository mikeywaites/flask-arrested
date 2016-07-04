# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


class ModelMixin(object):
    """ResourceMixin for use with SqlAlchemy models.  A list of model
    instances will be returned for processing.

    Results will also optionally be paginated when ``paginate=True`` is set.

    .. code-block:: python

        clas UserIndexApi(Resource, SQLAListResourceMixin):

            model = User
            paginate = True
            num_per_page = 10
            allow_empty = True
            paginator_class = SqlAlchemyPaginator

            def get_query(self):

                return get_all_users()


    .. seealso: :py:class:`.ListMixin`
    """

    model = None

    def get_session(self):
        raise NotImplementedError()

    def get_model(self):
        """Returns the model class associated with this multiple object
        mixin.

        :raises: TypeError
        :returns: Model class `model`
        """
        if not self.model:
            raise TypeError(
                "%s model cannot be None" % self.__class__.__name__)

        return self.model

    def get_query(self):
        """Get a query to use for a request.  This should return
        an :obj:`sqlalchemy.Query` instance and not a collection of
        model objects

        e.g:

            return db.session.query(FooModel).filter(bar=1)

        :returns: flask_sqlalchemy query object
        """
        raise NotImplementedError()
