from flask import Flask, request

from arrested import ArrestedAPI, Resource
from arrested.contrib.sql_alchemy import (
    DBListMixin,
    DBCreateMixin,
    DBObjectMixin,
)
from arrested.contrib.kim_arrested import KimEndpoint

from example.models import db, Character
from example.mappers import CharacterMapper

app = Flask(__name__)
app.config['DEBUG'] = True


def authenticated(endpoint):
    token_valid = request.args.get('token') == 'test-token'
    if not token_valid:
        endpoint.return_error(401)


def log_request(endpoint, response):

    app.logger.debug('request to characters resource made')
    return response


def is_admin(endpoint):

    endpoint.return_error(403)


api_v1 = ArrestedAPI(app, url_prefix='/v1', before_all_hooks=[authenticated])
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/code/example/starwars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

characters_resource = Resource('characters', __name__, url_prefix='/characters', after_all_hooks=[log_request])


class CharactersIndexEndpoint(KimEndpoint, DBListMixin, DBCreateMixin):

    name = 'list'
    many = True
    mapper_class = CharacterMapper

    def get_query(self):

        return db.session.query(Character)


class CharacterObjectEndpoint(KimEndpoint, DBObjectMixin):

    name = 'object'
    url = '/<string:obj_id>'
    mapper_class = CharacterMapper
    model = Character
    before_put_hooks = [is_admin]

    def get_query(self):

        return db.session.query(Character)


characters_resource.add_endpoint(CharactersIndexEndpoint)
characters_resource.add_endpoint(CharacterObjectEndpoint)
api_v1.register_resource(characters_resource)
