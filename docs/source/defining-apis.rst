Defining Apis
========================

Arrested provides everything you need to define your RESTFul api in flask.  It
comes with several built in classes for implmenting common rest paradigms as well as a flexible api
for implemening custom logic where requried.

The main component used when defining your endpoints are :class:`arrested.api.Resource`.  Resources provide specific handling for the HTTP methods
your endpoint needs to handle.

These classes are combined together to create ``Apis`` to suit your endpoints needs.  For example here's an endpoint that allows users to GET a list of user and also create new ones.

.. sourcecode:: python

    from arrested import Arrested, Api
    from arrested.contrib.oauth import OauthApi
    from arrested.contrib.kim import ListableResource, CreateableResource

    class UserIndexApi(OAuthApi, ListableResource, CreateableResource):
        url = '/users'
        endpoint_name = 'users.index'
        mapper_class = UserMapper
        scopes = ['read:users', 'write:users']
        methods = ['GET', 'POST']

        def get_objects(self):
            return get_users()

        def save_object(self):

            db.session.add(self.request.data)
            db.session.commit()

Here's another endpoint that only handles a GET request to return a user by id.

.. sourcecode:: python

    from arrested import Arrested, Api
    from arrested.contrib.oauth import OauthApi
    from arrested.contrib.kim import ObjectResource

    class UserObjectApi(OAuthApi, ObjectResource):

        url = '/users/<string:obj_id>'
        endpoint_name = 'users.index'
        mapper_class = UserMapper
        scopes = ['read:users', 'write:users']

        def get_object(self):
            return get_user_by_id(self.kwargs['obj_id'])


Making re-usable Api's
~~~~~~~~~~~~~~~~~~~~~~~


It's best practice to define common types of endpoints in your Api into classes you can re-use.  A common pattern in rest is to accept GET and POST requets to endpoints that describe more than one object IE /v1/users.
Perhaps we also have a /v1/companies endpoint as well as a /v1/posts endpoint.  Rather than re-defining you apis like


.. sourcecode:: python

    from arrested import Arrested, Api
    from arrested.contrib.oauth import OauthApi
    from arrested.contrib.kim import ListableResource, CreateableResource

    class UserIndexApi(OAuthApi, ListableResource, CreateableResource):
        ....


We could simply define a re-usable IndexApi class like

.. sourcecode:: python

    from arrested import Arrested, Api
    from arrested.contrib.oauth import OauthApi
    from arrested.contrib.kim import ListableResource, CreateableResource

    class IndexApi(OAuthApi, ListableResource, CreateableResource, ModelMixin):
        pass


    class UsersApi(IndexApi):

        url = '/users
        endpoint_name = 'user.index'
        mapper_class = UserMapper
        scopes = ['read:users', 'write:users']

        def get_query(self):

            return get_users()


    class CompaniesApi(IndexApi):

        url = '/companies'
        endpoint_name = 'company.index'
        mapper_class = UserMapper
        scopes = ['read:company', 'write:company']

        def get_query(self):

            return get_companies()
