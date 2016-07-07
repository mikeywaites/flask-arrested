from datetime import datetime, timedelta

from arrested.api import (
    ListableResource, CreateableResource, ObjectResource,
    UpdateableResource, DeleteableResource,
    PatchableResource)
from arrested.contrib.oauth import Api, OAuthApi

from sqlalchemy import Column, String, Boolean

from flask import session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider

from kim.mapper import Mapper
from kim.role import whitelist
from kim import field

db = SQLAlchemy()
oauth = OAuth2Provider()


def get_current_user():

    if 'id' in session:
        return User.query.get(session['id']).one_or_none()

    return None


def create_client():

    client = Client(
        name='Client', _default_scopes='read:users write:user')

    db.session.add(client)
    db.session.commit()

    return client


def create_users(session, num_users):

    users = []
    for i in range(num_users):
        users.append(User(name='user-%s' % i,
                          password='%s' % i,
                          id='%s' % i))
    session.add_all(users)
    session.commit()

    return users


def create_companies(session, num_companies):

    companies = []
    for i in range(num_companies):
        companies.append(Company(name='company-%s' % i,
                                 id='%s' % i))
    session.add_all(companies)
    session.commit()

    return companies


def create_access_token(user, token, scopes=None, client=None, expires=None):

    scopes = scopes or 'read:users write:users'
    client = client or create_client()
    expires = expires or datetime.now() + timedelta(days=5)

    tok = Token(
        id=gen_salt(10),
        access_token=token,
        refresh_token=gen_salt(10),
        token_type='bearer',
        _scopes=scopes,
        expires=expires,
        client_id=client.client_id,
        user_id=user.id,
    )

    db.session.add(tok)
    db.session.commit()

    return tok


@oauth.usergetter
def get_user(email, password, *args, **kwargs):
    user = User.query.filter_by(email=email).one_or_none()
    if user and user.verify_password(password):
        return user
    return None


@oauth.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()


@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=get_current_user(),
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()
    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = Token.query.filter_by(client_id=request.client.client_id,
                                 user_id=request.user.id)
    # make sure that every client has only one token connected to a user
    for t in toks:
        db.session.delete(t)

    expires_in = token.get('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        id=gen_salt(10),
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    db.session.add(tok)
    db.session.commit()
    return tok


class Client(db.Model):

    __tablename__ = 'clients'

    client_id = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.String(400))

    client_secret = db.Column(db.String(55), unique=True, index=True,
                              nullable=False)

    is_confidential = db.Column(db.Boolean)
    is_approved = db.Column(db.Boolean, default=False)

    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    def __init__(self, **kwargs):
        self.client_id = gen_salt(40)
        self.client_secret = gen_salt(40)
        super(Client, self).__init__(**kwargs)

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []


class Grant(db.Model):

    __tablename__ = 'grants'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')

    client_id = db.Column(
        db.String(40), db.ForeignKey('clients.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def __init__(self, **kwargs):
        super(Grant, self).__init__(**kwargs)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(db.Model):

    __tablename__ = 'tokens'

    id = db.Column(db.String, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('clients.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')

    # currently only bearer is supported
    token_type = db.Column(db.String(40))
    grant_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    def __init__(self, **kwargs):
        super(Token, self).__init__(**kwargs)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class User(db.Model):

    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    name = Column(String)
    password = Column(String)
    is_admin = Column(Boolean, default=False)


class Company(db.Model):

    __tablename__ = 'company'
    id = Column(String, primary_key=True)
    name = Column(String)


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


class TestUsersIndex(Api, ListableResource, CreateableResource):

    mapper_class = UserMapper
    url = '/users'
    model = User
    endpoint_name = 'users.index'
    serialize_role = 'public'

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


class TestApi(OAuthApi):

    def get_session(self):

        return db.session

    def get_oauth(self):
        return oauth


class TestCompanyIndex(TestApi, ListableResource, CreateableResource):

    mapper_class = CompanyMapper
    model = Company
    url = '/companies'
    endpoint_name = 'companies.index'
    scopes = ['read:companies', 'write:companies']

    def get_query(self):

        db = self.get_session()
        return db.query(self.model)


class TestAdminUserIndexApi(TestApi, CreateableResource):

    mapper_class = UserMapper
    model = User
    url = '/admins'
    endpoint_name = 'admin.index'
    write_scopes = ['write:users', 'write:admins']
    read_scopes = ['read:companies', 'read:users']
    serialize_role = 'public'

    def save_object(self):
        self.obj.id = '%s-id' % self.obj.name
        super(TestAdminUserIndexApi, self).save_object()
