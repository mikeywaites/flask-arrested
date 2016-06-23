# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from kim.exception import MappingInvalid

from arrested.api import BaseListableResource, BaseCreateableResource
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

    def handle(self, data):
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

    def handle(self, data):
        """TODO(mike) Docs
        """

        try:
            if self.many:
                return self.mapper.many(raw=self.raw, **self.mapper_kwargs) \
                    .marshal(data, role=self.role)
            else:
                return self.mapper(data=data, raw=self.raw, **self.mapper_kwargs) \
                    .marshal(role=self.role)
        except MappingInvalid as e:
            self.errors = e.errors


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


class ListableResource(KimResourceMixin, BaseListableResource):
    """TODO(mike) Docs
    """

    def get_response_handler_params(self, **params):
        """TODO(mike) Docs
        """
        params = self.get_mapper_params(**params)
        params = super(ListableResource, self) \
            .get_response_handler_params(**params)

        params['many'] = True
        params['role'] = self.serialize_role

        return params


class CreateableResource(KimResourceMixin, BaseCreateableResource):
    """TODO(mike) Docs
    """

    # TODO(mike) There's probably a better name for this.
    serialize_create_role = None

    def get_response_handler_params(self, **params):
        """TODO(mike) Docs
        """
        params = self.get_mapper_params(**params)
        params = super(CreateableResource, self) \
            .get_response_handler_params(**params)

        params['many'] = False
        params['role'] = self.serialize_create_role or self.serialize_role

        return params

    def get_request_handler_params(self, **params):
        """TODO(mike) Docs
        """

        params = self.get_mapper_params(**params)
        params = super(CreateableResource, self) \
            .get_request_handler_params(**params)

        params['role'] = self.marshal_role

        return params
