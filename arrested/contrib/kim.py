# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


from arrested.api import ListableResource


class ListableResource(ListableResource):

    serialize_role = '__default__'
    mapper_class = None
    raw = False

    def get_role(self):

        return self.serialize_role

    def get_response_hanlder_params(self, **params):
        """
        """
        params = super(ListableResource, self) \
            .get_repsonse_handler_params(**params)

        params['many'] = True
        params['role'] = self.get_role()
        params['mapper_class'] = self.mapper_class
        params['raw'] = self.raw

        return params
