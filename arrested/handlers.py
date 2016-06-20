# flask_arrested/__init__.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import json

from kim.exception import MappingInvalid


class Handler(object):
    """Handler classes are an interface between your Arrested Apis and your
    choosen method of marshaling and serializing data.  Each Api defines
    `RequestHandler` and `ResponseHandler` classes derived
    from :py:class:`Handler`.

    Inline with Arrested's ethos of not making assumptions about how the
    user want's to implement their RESTFul api, Handlers provide a simple and
    flexibile way to handle data on an Api by Api basis.

    .. codeblock:: python

        from arrested import Api
        from arrested.handlers import Handler

        class MyRequestHandler(Handler):

            def __init__(self, object=None, *args, **params):
                self.object = object
                super(MyRequestHandler, self).__init__(*args, **params)

            def handle(self, data):

                for key, value in data.items():

                    setattr(self.object, key, value)

                return self.object

        class MyResponseHandler(Handler):

            def handle(self, object):

                obj = {
                    'key': object.key,
                    'other_key': object.other_key
                }

                return key

        class MyApi(Api):

            request_handler = MyRequestHandler
            reponse_handler = MyResponseHandler

    """

    def __init__(self, **params):
        """Create a new instance of a Handler.

        :param params: Dict contaniing handler specific options.
        """
        self.params = params
        self.data = None
        self.errors = None

    def to_json(self):
        """Serialize `data` to a JSON string.
        """

        return json.dumps(self.data)

    def handle(self, data):
        """Invoke the handler to process the provided data.  Concrete classes
        should override this method to provide specific capabilties for the
        choosen method of marshaling and serializing data.

        Here's an example of a RequestHandler integrating with the Kim library.

        .. codeblock:: python

            def handle(self, data):
                try:
                    if self.many:
                        return self.mapper.many(raw=self.raw,
                                                **self.mapper_kwargs) \
                            .marshal(data, role=self.role)
                    else:
                        return self.mapper(data=data, raw=self.raw,
                                           **self.mapper_kwargs) \
                            .marshal(role=self.role)
                except MappingInvalid as e:
                    self.errors = e.errors

        .. seealso:
            :meth:`process`

        """
        raise NotImplementedError(
            '%s must implement handle method' % self.__class__.__name__)

    def process(self, data):
        """Process the provided data and invoke :meth:`handle` method for this
        Handler class.

        :params data: The data the handler should process

        .. codeblock:: python

            def post(self, *args, **kwargs):

                self.request = self.get_request_handler()
                self.request.process(self.get_data())

                return self.get_create_response()


        .. seealso:
            :meth:`process`
        """
        self.data = self.handle(data)


class KimHandler(Handler):

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
