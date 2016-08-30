Features
----------

- Flexibile system for defining re-usable APIS
- Support for SQLAlchemy out of the box
- Flexibile Marshaling and Serilialization interface.  Use your favourite tools to handle data into and out from your API.
- Support for popular auth implementations such as `Flask-Oauthlib <https://github.com/lepture/flask-oauthlib>`_
- Flexibile query param parsing

Library Installation
--------------------

.. code-block:: bash

   $ pip install arrested


Getting Started
--------------------

Here's a very basic working example of using Flask-Arrested to define an
SQLAlchemy backed User rest api.  You can find the full code used in this example here `flask-arrested-example <https://github.com/oldstlabs/flask-arrested-example>`_

.. code-block:: python

    import os

    from flask import Flask

    from arrested import Arrested
    from arrested.api import (
        Api, ListableResource, CreateableResource,
        ObjectResource, PatchableResource,
        UpdateableResource, DeleteableResource)

    from .models import db, User, Company
    from .mappers import UserMapper, CompanyMapper

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            'sqlite:////opt/code/userlist.db')


    db.init_app(app)
    api = Arrested(app)


    class UsersIndexApi(Api, ListableResource, CreateableResource):

        url = '/users'
        endpoint_name = 'users.index'
        scopes = ['read:users', 'write:users']
        mapper_class = UserMapper

        def get_query(self):

            return User.get_users()


    class UserObjectApi(Api, ObjectResource, UpdateableResource,
                        DeleteableResource, PatchableResource):

        url = '/users/<string:user_id>'
        endpoint_name = 'users.object'
        scopes = ['read:users', 'write:users']
        mapper_class = UserMapper

        def get_query(self):

            return User.get_user_by_id(self.kwargs['user_id'])


    class CompaniesIndexApi(Api, ListableResource, CreateableResource):

        url = '/companies'
        endpoint_name = 'companies.index'
        scopes = ['read:companies', 'write:companies']
        mapper_class = CompanyMapper

        def get_query(self):

            return Company.get_companies()


    class CompanyObjectApi(Api, ObjectResource, UpdateableResource,
                           DeleteableResource, PatchableResource):

        url = '/companies/<string:company_id>'
        endpoint_name = 'companies.object'
        scopes = ['read:companies', 'write:companies']
        mapper_class = CompanyMapper

        def get_query(self):

            return Company.get_user_by_id(self.kwargs['company_id'])

    api.register(UsersIndexApi)
    api.register(UserObjectApi)
    api.register(CompaniesIndexApi)
    api.register(CompanyObjectApi)
