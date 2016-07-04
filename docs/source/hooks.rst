Request Hooks
==================

Arrested Provides a system for defining hooks that are run on a per request, per api basis.  Under the hood that resolve to
flask before_request and after_hooks wrapped in some logic to selectively apply the hook given that the URL and HTTP method are valid.

.. sourcecode:: python

    class UsersIndexApi(Api, ListableResource, CreateableResource):

        methods = ['GET']
        urls = '/users'
        endpoint_name = 'users.index'
        response_handler = KimResponseHandler
        request_handler = KimRequestHandler

        @hook(methods=['GET', 'POST'], type_='before_request')
        def log_request(self):

            logger.debug('request made')

        @hook(methods=['POST'], type_='after_request')
        def send_email(self, request):

            send_email()

            return request
