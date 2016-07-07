import pytest
import json

from flask import url_for

from arrested.contrib.oauth import OAuthApi

from .api import (
    oauth, TestCompanyIndex, create_users, TestAdminUserIndexApi,
    create_access_token, create_companies)


@pytest.yield_fixture(scope='function')
def oauth_api(request, flask_app, api):

    oauth.init_app(flask_app)

    api.register(TestCompanyIndex)
    api.register(TestAdminUserIndexApi)

    yield oauth_api


def test_get_index_api_no_access_token(oauth_api, client, db_session):

    u1, u2 = create_users(db_session, 2)

    resp = client.get(url_for('api.companies.index'))

    assert resp.status_code == 401


def test_get_index_api(oauth_api, client, db_session):

    u1, = create_users(db_session, 1)
    c1, c2 = create_companies(db_session, 2)
    token = create_access_token(u1, 'foo-token', scopes='read:companies write:companies')

    resp = client.get(
        url_for('api.companies.index', access_token=token.access_token))

    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    data = json.loads(resp.data.decode('utf-8'))
    assert data == {
        'meta': {
            'total_pages': 1,
            'total_objects': 2,
            'per_page': 10,
            'current_page': 1,
            'next_page': None,
            'prev_page': None,
        },
        'payload': [
            {'id': c1.id, 'name': c1.name},
            {'id': c2.id, 'name': c2.name}
        ]
    }


def test_post_index_api_write_scopes(oauth_api, client, db_session):

    u1, = create_users(db_session, 1)
    token = create_access_token(
        u1, 'foo-token',
        scopes='read:companies read:user write:users write:admins')

    data = {
        'name': 'My Admin',
        'password': '123123',
        'is_admin': True
    }
    resp = client.post(
        url_for('api.admin.index', access_token=token.access_token),
        data=json.dumps(data), content_type='application/json')

    assert resp.status_code == 201

    resp_data = json.loads(resp.data.decode('utf-8'))
    exp = {
        'payload': {
            'id': resp_data['payload']['id'], 'name': 'My Admin',
            'is_admin': True
        }
    }

    assert resp_data == exp


def test_get_invalid_scopes(oauth_api, client, db_session):

    u1, = create_users(db_session, 1)
    c1, c2 = create_companies(db_session, 2)
    token = create_access_token(u1, 'foo-token', scopes='read:foo')

    resp = client.get(
        url_for('api.companies.index', access_token=token.access_token))

    assert resp.status_code == 401


def test_oauth_api_requires_oauth_object(oauth_api, client, db_session):

    oauth = OAuthApi()
    with pytest.raises(NotImplementedError):
        oauth.get_oauth()
