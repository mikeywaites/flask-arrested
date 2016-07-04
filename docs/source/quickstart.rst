Quickstart
=============

Here's a very basic working example of using Flask-Arrested to define an
SQLAlchemy back User rest api.  The Example uses the Kim - JSON Marhsaling and Serialization framework
to process both incoming and outgoing data.

.. sourcecode:: python

    from flask import Flask
    from arrested import Api
    from arrested.contrib.kim import ListableResource, CreateableResource
    from arrested.contrib.oauth import OAuthApi
    from arrested.mixins import ModeListMixin

    from kim import Mapper, field

    app = Flask(__name__)
    api = Api(app)


    # define our Kim mappers

    class CompanyMapper(Mapper):
        __type__ = Company

        id = field.String()
        name = field.String()
        email = field.String()
        company = field.Nested('CompanyMapper')


    class UserMapper(Mapper):
        __type__ = User

        id = field.String()
        name = field.String()
        email = field.String()
        company = field.Nested('CompanyMapper')


    # define our Apis
    class IndexApi(OauthApi, ListableResource, CreateableResource, ModelMixin):
        pass

    class ObjectApi(OauthApi, ObjectResource, PatchableResource,
                    DeleteableResource, UpdateableResource, ModelObjectMixin):
        pass

    class UsersIndexApi(IndexApi):

        urls = '/users'
        endpoint_name = 'users.index'
        scopes = ['read:users', 'write:users']
        mapper_class = UserMapper

        def get_query(self):

            return get_users()


    class UserObjectApi(ObjectApi):

        urls = '/users/<string:user_id>'
        endpoint_name = 'users.index'
        scopes = ['read:users', 'write:users']
        mapper_class = UserMapper

        def get_query(self):

            return get_user_by_id(self.kwargs['user_id'])


    class CompaniesIndexApi(IndexApi):

        urls = '/companies'
        endpoint_name = 'companies.index'
        scopes = ['read:companies', 'write:companies']
        mapper_class = CompanyMapper

        def get_query(self):

            return get_companies()


    class CompanyObjectApi(ObjectApi):

        urls = '/companies/<string:company_id>'
        endpoint_name = 'companies.index'
        scopes = ['read:companies', 'write:companies']
        mapper_class = CompanyMapper

        def get_query(self):

            return get_company_by_id(self.kwargs['comapny_id'])


    api.register(UsersIndexApi)
    api.register(UserObjectApi)
    api.register(CompaniesIndexApi)
    api.register(CompanyObjectApi)

    if __name__ == "__main__":

        app.run()
