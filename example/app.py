#from flask import Flask, request
#
#from arrested import ArrestedAPI, Resource
#from arrested.contrib.sqa import (
#    DBListMixin,
#    DBCreateMixin,
#    DBObjectMixin,
#)
#from arrested.contrib.kim import KimEndpoint
#
#from example.models import db, Character
#from example.mappers import CharacterMapper
#
#app = Flask(__name__)
#app.config['DEBUG'] = True
#
#
#def authenticated(endpoint):
#    token_valid = request.args.get('token') == 'test-token'
#    if not token_valid:
#        endpoint.return_error(401)
#
#
#def log_request(endpoint, response):
#
#    app.logger.debug('request to characters resource made')
#    return response
#
#
#def is_admin(endpoint):
#
#    endpoint.return_error(403)
#
#
#api_v1 = ArrestedAPI(app, url_prefix='/v1', before_all_hooks=[authenticated])
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/code/example/starwars.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db.init_app(app)
#
#characters_resource = Resource('characters', __name__, url_prefix='/characters', after_all_hooks=[log_request])
#
#
#class CharactersIndexEndpoint(KimEndpoint, DBListMixin, DBCreateMixin):
#
#    name = 'list'
#    many = True
#    mapper_class = CharacterMapper
#
#    def get_query(self):
#
#        return db.session.query(Character)
#
#
#class CharacterObjectEndpoint(KimEndpoint, DBObjectMixin):
#
#    name = 'object'
#    url = '/<string:obj_id>'
#    mapper_class = CharacterMapper
#    model = Character
#    before_put_hooks = [is_admin]
#
#    def get_query(self):
#
#        return db.session.query(Character)
#
#
#characters_resource.add_endpoint(CharactersIndexEndpoint)
#characters_resource.add_endpoint(CharacterObjectEndpoint)
#api_v1.register_resource(characters_resource)


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
