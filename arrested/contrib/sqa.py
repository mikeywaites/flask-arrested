from math import ceil


class SqlAlchemyPaginator(object):

    def __init__(self, query, page, per_page=20):
        self.query = query
        self.page = page
        self.per_page = per_page

        start = (page - 1) * per_page
        stop = page * per_page
        self.items = query.slice(start, stop).all()

        # No need to count if we're on the first page and there are fewer
        # items than we expected.
        if page == 1 and len(self.items) < per_page:
            self.total = len(self.items)
        else:
            self.total = query.order_by(None).count()

    @property
    def next_page(self):
        """The total number of pages"""
        if self.page < self.pages:
            return self.page + 1
        else:
            return None

    @property
    def prev_page(self):
        """The total number of pages"""
        return self.page - 1 or None

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages
