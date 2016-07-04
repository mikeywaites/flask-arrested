# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from kim.exception import MappingInvalid

from arrested.handlers import Handler


class KimHandler(Handler):
    """TODO(mike) Docs
    """

    def __init__(self, *args, **params):
        """TODO(mike) Docs
        """
        super(KimHandler, self).__init__(*args, **params)

        self.mapper_class = params.pop('mapper_class', None)
        self.mapper_kwargs = params.pop('mapper_kwargs', {})
        self.role = params.pop('role', '__default__')
        self.many = params.pop('many', False)
        self.raw = params.pop('raw', False)
        self.partial = params.pop('partial', False)

    @property
    def mapper(self):
        """TODO(mike) Docs
        """
        if self.mapper_class is None:
            raise Exception('KimHandler requires a Kim mapper_class')

        return self.mapper_class


class KimResponseHandler(KimHandler):
    """TODO(mike) Docs
    """

    def handle(self, data, **kwargs):
        """TODO(mike) Docs
        """

        if self.many:
            return self.mapper.many(raw=self.raw, **self.mapper_kwargs) \
                .serialize(data, role=self.role)
        else:
            return self.mapper(obj=data, raw=self.raw, **self.mapper_kwargs) \
                .serialize(role=self.role)


class KimRequestHandler(KimHandler):
    """TODO(mike) Docs
    """

    def handle(self, data, **kwargs):
        """TODO(mike) Docs
        """

        obj = kwargs.get('instance', None)

        try:
            if self.many:
                return self.mapper.many(raw=self.raw, **self.mapper_kwargs) \
                    .marshal(data, role=self.role)
            else:
                return self.mapper(data=data, obj=obj, raw=self.raw,
                                   partial=self.partial,
                                   **self.mapper_kwargs) \
                    .marshal(role=self.role)
        except MappingInvalid as e:
            self._errors = e.errors


class KimResourceMixin(object):

    marshal_role = '__default__'
    serialize_role = '__default__'
    mapper_class = None
    raw = False
    response_handler = KimResponseHandler
    request_handler = KimRequestHandler

    def get_mapper_params(self, **params):
        """TODO(mike) Docs
        """
        params['mapper_class'] = self.mapper_class
        params['raw'] = self.raw

        return params
