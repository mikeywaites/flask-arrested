# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from flask import request


class ListMixin(object):
    """ListMixin provides :py::class:`Resource` apis with capabilities for
    handling GET requests as well as utilities for paginating results
    """

    paginate = True
    num_per_page = None
    paginated = None
    allow_empty = True
    page_kwarg = 'page'
    per_page_param = 'per_page'
    paginator_class = None

    def get_num_per_page(self):
        """ Get the number of items to paginate by, or
        ``None`` for no pagination.
        """
        per_page = request.args.get(self.per_page_param, self.num_per_page)
        if self.paginate:
            try:
                return int(per_page)
            except (ValueError, TypeError):
                return self.num_per_page

    def get_page(self):
        """Return the current page number set at `page_kwarg` in
        :obj:`flask.request` or return 1 for the first page
        :returns: int
        """
        try:
            val = int(request.args.get(self.page_kwarg, 1))
            return val or 1
        except ValueError:
            return 1

    def get_objects(self):
        """Returns a queryset of objects.  If pagination is enabled
        then the query object will be paginated.
        """
        raise NotImplementedError(
            'get_objects must be defined by a concrete class')

    def get_paginator(self):
        """TODO(mike) Docs
        """
        return self.paginator_class()


class CreateMixin(object):

    pass


class UpdateMixin(object):

    pass


class PatchMixin(object):

    pass


class DeleteMixin(object):

    pass


class SqlAlchemyPaginator(object):

    def __init__(self, query, page, per_page=20):
        self.query = query
        self.page = page
        self.per_page = page
        self.error_out

        start = (page - 1) * per_page
        stop = page * per_page
        self.items = query.slice(start, stop).all()

        # No need to count if we're on the first page and there are fewer
        # items than we expected.
        if page == 1 and len(self.items) < per_page:
            self.total = len(self.items)
        else:
            self.total = query.order_by(None).count()


class ModelListMixin(ListMixin):
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
    paginator_class = SqlAlchemyPaginator

    def get_query(self):

        raise NotImplementedError('concrete classes must implement get_query')

    def get_objects(self):
        """Return a list of instances produced from :meth:`get_query` and
        optionally paginate them.

        """
        query = self.get_query()
        page_size = self.get_paginate_by(query)

        if page_size:
            self.paginated = self.get_paginator(
                query,
                self.get_page(),
                page_size,
                not self.allow_empty
            )
            return self.paginated.items
        else:
            return query.all()
