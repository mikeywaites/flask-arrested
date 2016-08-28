Getting Started
================

Here's a very basic working example of using Flask-Arrested to define an
SQLAlchemy backed User rest api.

You can find the full code used in this example here.

Install the `arrested` package to whatever flavour container or virtuaenv etc your app is using.

.. sourcecode:: python

    pip install arrested


.. sourcecode:: python

    import os

    from flask import Flask

    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import Column, String, Boolean

    from kim.mapper import Mapper
    from kim.role import whitelist
    from kim import field

    from arrested import Arrested
    from arrested.api import (
        Api, ListableResource, CreateableResource,
        ObjectResource, PatchableResource,
        UpdateableResource, DeleteableResource)

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            'sqlite:////opt/code/example.db')

    db = SQLAlchemy(app)
    api = Arrested(app)


    class User(db.Model):

        __tablename__ = 'users'
        id = Column(String, primary_key=True)
        name = Column(String)
        password = Column(String)
        is_admin = Column(Boolean, default=False)
        company_id = Column(String, db.ForeignKey('company.id'))

        company = db.relationship('Company')

        @classmethod
        def get_users(cls):
            query = db.session.query
            stmt = query(cls) \
                .order_by(cls.name)

            return stmt

        @classmethod
        def get_user_by_id(cls, id_):
            query = db.session.query
            stmt = query(cls) \
                .filter(cls.id == id_)

            return stmt


    class Company(db.Model):

        __tablename__ = 'company'
        id = Column(String, primary_key=True)
        name = Column(String)

        @classmethod
        def get_companies(cls):
            query = db.session.query
            stmt = query(cls) \
                .order_by(cls.name)

            return stmt

        @classmethod
        def get_company_by_id(cls, id_):
            query = db.session.query
            stmt = query(cls) \
                .filter(cls.id == id_)

            return stmt


Defining Endpoints
~~~~~~~~~~~~~~~~~~~~~~

Now we've got our models setup we want to expose some endpoints to allow our
users to start interacting with our user company objects.  Below we define index API's to expose
GET endpoints for retrieving lists of users and companys as well as POST endpoints for creating new objects.

In addition to these Index Api's, we also set up ObjectApi endpoints to support retrieving single objects using an id via GET request.
PUT and PATCH support provide the ability to update the existing objects and DELETE obviously allows our users to delete.

.. sourcecode:: python


    class UserMapper(Mapper):
        __type__ = User

        id = field.String(read_only=True)
        name = field.String()
        password = field.String()
        is_admin = field.Boolean(required=False, default=False)

        __roles__ = {
            'public': whitelist('name', 'id', 'is_admin')
        }


    class CompanyMapper(Mapper):
        __type__ = User

        id = field.String(read_only=True)
        name = field.String()

        __roles__ = {
            'public': whitelist('name', 'id')
        }


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
