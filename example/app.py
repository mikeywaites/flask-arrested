import json

from werkzeug.exceptions import NotFound
from flask import Flask

from arrested import ArrestedAPI, Resource
from arrested.contrib.sqa import (
    DBListMixin,
    DBCreateMixin,
    DBObjectMixin,
    DBUpdateMixin
)
from arrested.contrib.kim import KimEndpoint

from example.models import db, Character
from example.mappers import CharacterMapper


app = Flask(__name__)
api_v1 = ArrestedAPI(app, url_prefix='/v1')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/code/example/starwars.db'
db.init_app(app)

characters_resource = Resource('characters', __name__, url_prefix='/characters')


@app.errorhandler(NotFound)
def handle_bad_request(e):
    e.response.data = json.dumps({'error': 'Not Found'})
    return e.response


class CharactersEndpoint(KimEndpoint, DBListMixin, DBCreateMixin):

    name = 'list'
    many = True
    mapper_class = CharacterMapper

    def get_query(self):

        return db.session.query(Character)


class CharacterObjectEndpoint(KimEndpoint, DBObjectMixin, DBUpdateMixin):

    name = 'object'
    url = '/<string:obj_id>'
    mapper_class = CharacterMapper

    def get_query(self):

        return db.session.query(Character)


characters_resource.add_endpoint(CharactersEndpoint)
characters_resource.add_endpoint(CharacterObjectEndpoint)
api_v1.register_resource(characters_resource)
