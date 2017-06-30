import json
import pytest
import datetime

from flask import url_for
from kim import Mapper, field
from kim.mapper import _MapperConfig
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound

from arrested import Resource, ArrestedAPI
from arrested.contrib.sqa import (
    DBListMixin,
    DBCreateMixin,
    DBObjectMixin,
    DBUpdateMixin
)
from arrested.contrib.kim import KimEndpoint


db = SQLAlchemy()

class Character(db.Model):

    __tablename__ = 'character'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class CharacterMapper(Mapper):

    __type__ = Character

    id = field.Integer(read_only=True)
    name = field.String()
    created_at = field.DateTime(read_only=True)


@pytest.yield_fixture()
def alchemy_api(request, app):

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/code/tests/tests.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

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

    characters_resource = Resource('characters', __name__, url_prefix='/characters')
    characters_resource.add_endpoint(CharactersEndpoint)
    characters_resource.add_endpoint(CharacterObjectEndpoint)

    api_v1 = ArrestedAPI(app, url_prefix='/v1')
    api_v1.register_resource(characters_resource)

    db.create_all()
    yield
    db.session.remove()
    db.drop_all()


def test_get_list(alchemy_api, client):
    """Functional test ensuring that DBListMixin retuns the expected response."""

    luke = Character(name='Luke Skywalker')
    db.session.add(luke)
    db.session.commit()

    resp = client.get(url_for('characters.list'))

    assert resp.status_code == 200
    exp = {
        'payload': [
            CharacterMapper(obj=luke).serialize()
        ]
    }
    assert json.loads(resp.data) == exp


def test_get_object(alchemy_api, client):
    """Functional test ensuring that DBObjectMixin retuns the expected response."""

    luke = Character(name='Luke Skywalker')
    db.session.add(luke)
    db.session.commit()

    resp = client.get(url_for('characters.object', obj_id=luke.id))

    assert resp.status_code == 200
    exp = {
        'payload': CharacterMapper(obj=luke).serialize()
    }
    assert json.loads(resp.data) == exp


def test_create_object(alchemy_api, client):
    """Functional test ensuring that DBCreateMixin saves our new instance and returns
    the expected reponse"""

    luke = Character(name='Luke Skywalker')
    db.session.add(luke)
    db.session.commit()

    data = {'name': 'Obe Wan'}
    resp = client.post(
        url_for('characters.list'),
        data=json.dumps(data),
        content_type='application/json'
    )

    assert resp.status_code == 201
    resp_data = json.loads(resp.data)
    new_obj = Character.query.get(resp_data['payload']['id'])
    assert new_obj.id is not None
    assert new_obj.name == 'Obe Wan'
    exp = {'payload': CharacterMapper(obj=new_obj).serialize()}
    assert resp_data == exp
