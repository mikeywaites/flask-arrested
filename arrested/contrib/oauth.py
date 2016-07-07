from flask import request

from ..api import Api


class OAuthApi(Api):
    """decorates all HTTP methods with :func`authentication_required` which
    ensures that each `request` has an authenticated session.

    This resource also provides a helper method :meth:`get_user` which
    will return the currently logged in user.

    .. seealso::
        :func:`.authentication_required`

    """

    scopes = []

    def get_oauth(self):
        """TODO(mike) Docs
        """

        raise NotImplementedError('OAuthApi requires the get_oauth'
                                  ' method be overridden')

    def dispatch_request(self, *args, **kwargs):
        """TODO(mike) Docs
        """

        if request.method in ['POST', 'DELETE', 'PUT', 'PATCH']:
            scope_method_name = 'write_scopes'
        else:
            scope_method_name = 'read_scopes'

        _scopes = getattr(self, scope_method_name, self.scopes)

        oauth = self.get_oauth()

        @oauth.require_oauth(*_scopes)
        def inner_dispatch():

            return super(OAuthApi, self).dispatch_request(*args, **kwargs)

        return inner_dispatch()

    def get_user(self):
        """TODO(mike) Docs
        """

        return request.oauth.user
