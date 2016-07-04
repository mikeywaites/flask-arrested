from arrested import Api
from arrested.api import (
    ListableResource, CreateableResource, ObjectResource,
    UpdateableResource, DeleteableResource,
    PatchableResource)

from sqlalchemy import Column, String

from flask_sqlalchemy import SQLAlchemy

from kim.mapper import Mapper
from kim import field

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    name = Column(String)
    password = Column(String)


class UserMapper(Mapper):
    __type__ = User

    id = field.String(read_only=True)
    name = field.String()
    password = field.String()

    __roles__ = {
        'public': ['name', 'id']
    }


class TestUsersIndex(Api, ListableResource, CreateableResource):

    mapper_class = UserMapper
    url = '/users'
    model = User
    endpoint_name = 'users.index'
    serialize_role = 'public'
    marshal_role = 'public'

    def save_object(self):
        self.obj.id = '%s-id' % self.obj.name
        super(TestUsersIndex, self).save_object()

    def get_session(self):

        return db.session

    def get_query(self):

        db = self.get_session()
        return db.query(self.model)


class TestUserObjectApi(Api, ObjectResource, UpdateableResource,
                        DeleteableResource, PatchableResource):

    mapper_class = UserMapper
    model = User
    url = '/users/<string:obj_id>'
    endpoint_name = 'users.object'
    serialize_role = 'public'

    def get_session(self):

        return db.session

    def get_query(self):

        db = self.get_session()
        return db.query(self.model)
