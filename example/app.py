from flask import Flask

from arrested import (
    ArrestedAPI, Resource, Endpoint, GetListMixin, CreateMixin,
    GetObjectMixin, PutObjectMixin, DeleteObjectMixin, ResponseHandler
)

from example.models import db, Character

app = Flask(__name__)
api_v1 = ArrestedAPI(app, url_prefix='/v1')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/code/example/starwars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

characters_resource = Resource('characters', __name__, url_prefix='/characters')


def character_serializer(obj):
    return {
        'id': obj.id,
        'name': obj.name,
        'created_at': obj.created_at.isoformat()
    }


class DBResponseHandler(ResponseHandler):

    def __init__(self, endpoint, *args, **params):
        super(DBResponseHandler, self).__init__(endpoint, *args, **params)

        self.serializer = params.pop('serializer', None)

    def handle(self, data, **kwargs):

        if isinstance(data, list):
            objs = []
            for obj in data:
                objs.append(self.serializer(obj))
            return objs
        else:
            return self.serializer(data)


class CharactersIndexEndpoint(Endpoint, GetListMixin, CreateMixin):

    name = 'list'
    many = True
    response_handler = DBResponseHandler

    def get_response_handler_params(self, **params):

        params['serializer'] = character_serializer
        return params

    def get_objects(self):

        characters = db.session.query(Character).all()
        return characters

    def save_object(self, obj):

        character = Character(**obj)
        db.session.add(character)
        db.session.commit()
        return character


class CharacterObjectEndpoint(Endpoint, GetObjectMixin,
                              PutObjectMixin, DeleteObjectMixin):

    name = 'object'
    url = '/<string:obj_id>'
    response_handler = DBResponseHandler

    def get_response_handler_params(self, **params):

        params['serializer'] = character_serializer
        return params

    def get_object(self):

        obj_id = self.kwargs['obj_id']
        obj = db.session.query(Character).filter(Character.id == obj_id).one_or_none()
        if not obj:
            payload = {
                "message": "Character object not found.",
            }
            self.return_error(404, payload=payload)

        return obj

    def update_object(self, obj):

        data = self.request.data
        allowed_fields = ['name']

        for key, val in data.items():
            if key in allowed_fields:
                setattr(obj, key, val)

        db.session.add(obj)
        db.session.commit()

        return obj

    def delete_object(self, obj):

        db.session.delete(obj)
        db.session.commit()


characters_resource.add_endpoint(CharactersIndexEndpoint)
characters_resource.add_endpoint(CharacterObjectEndpoint)
api_v1.register_resource(characters_resource)
