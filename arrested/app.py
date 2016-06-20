# arrested/api.py
# Copyright (C) 2014-2015 the Flask-Arrested authors and contributors
# <see AUTHORS file>
#
# This module is part of Flask-Arrested and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


class Arrested(object):
    """Arrested application object.  This class provides the typical
    flask appliaction initialisation api.

    Instantiating the Arrested object can be done in one of two ways.  You
    may pass the :py:class:``flask.Flask`` application object
    to the construtor::

    .. codeblock:: python

        from flask import Flask
        from arrested import Arrested

        app = Flask(__name__)
        api = Arrested(app)

        api.register(UserIndexApi)

    Or the flask application object may be lazily loaded.  This is useful when
    users make use of the factory method for generating flask objects.

    You may define all your Api Resources in a module called myproject.api.
    This file might look something like the following

    .. codeblock:: python

        from arrested import Arrested, Api

        api = Arrested()

        class UserIndexApi(Api):

            url = '/users'

        api.regsiter(UserIndexApi)


    In our flask factory function we'd simply need to import the api object
    and register it with our flask app object using ``api.init_app()`` method.

    .. codeblock:: python

        from flask import Flask

        from myproject.api import api

        def create_app(config_name='dev'):
            app = Flask(__name__)
            api.init_app(app)

            return app

    """

    def __init__(self, app=None, name='api', url_prefix='/v1'):
        """ Construct a new instance of an Arrested object

        :param app: Flask application object
        :param name: name namespaced API routes.
        :param url_prefix: prefix all resource urls.
        """
        self.app = None
        self.url_prefix = url_prefix
        self.name = name

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """initialise the flask app object against an instance of
        :py:class:`Arrested`.

        :param app: Flask application object
        """

        self.app = app

    def get_api_url(self, url=None):
        """Contruct a url for the given api.  If ``self.url_prefix``
        has been set by the user, the returned url will be prefixed.

        :param resource: :py:class:`arrested.Api`
        """
        if self.url_prefix is not None:
            url = self.url_prefix + url or self.url
        else:
            url = url or self.url

        return url

    def register(self, _Api, url=None):
        """Register a new endpoint for a resource in this API.

        We don't make use of :py:class`flask.Blueprint` here as
        once the blueprint has been registered with the flask app
        object subsequent calls to Blueprint.add_url_rule will not
        actually be added to the apps url_map.

        .. codeblock:: python

            api.regiter(UserIndexApi)

        :param _Api: :py:class:`Api` class being registered
        :param url: provide a url to override the _Api.url param
        """

        assert self.app is not None, "You must register a flask app instance" \
                                     " before registering resources"

        setattr(_Api, 'app', self)

        view = _Api.as_view(_Api.endpoint_name)

        endpoint = _Api()
        for func in endpoint.get_before_hooks():
            self.app.before_request(func)

        for func in endpoint.get_after_hooks():
            self.app.after_request(func)

        self.app.add_url_rule(
            self.get_api_url(url or _Api.url),
            '%s.%s' % (self.name, _Api.endpoint_name),
            view, methods=_Api.methods)
