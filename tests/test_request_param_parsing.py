import json
import iso8601
import datetime

from flask import url_for

from arrested import Arrested
from arrested.api import Api, ListableResource
from arrested.api import RequestParamParser


def _build_endpoint(flask_app):

    api = Arrested(flask_app)

    class MyTestResource(Api, ListableResource):

        endpoint_name = 'test_resource'
        url = '/tests'
        param_parser_class = RequestParamParser

        def get(self, *args, **kwargs):
            str_param = self.param('test_str').str()
            int_param = self.param('test_int').int()
            date_param = self.param('test_date').date()
            iso_param = self.param('test_iso').iso8601()
            if str_param:
                return json.dumps({
                    "test_str": str_param,
                    "test_int": int_param,
                    "test_date": date_param.strftime('%Y-%m-%d'),
                    "test_iso": iso_param.isoformat(),
                })
            else:
                return json.dumps({'test': 'true'})

    api.register(MyTestResource)


def test_request_parsing_via_api(flask_app, client):

    _build_endpoint(flask_app)
    params = {
        'test_str': 'one',
        'test_int': 1,
        'test_date': '2016-01-01',
        'test_iso': '2007-01-25T12:00:00+00:00'
    }

    resp = client.get(url_for('api.test_resource', **params))
    assert resp.status_code == 200
    data = json.loads(resp.data.decode('utf-8'))

    assert data == params


def test_str_parser_missing_param(flask_app, client):

    _build_endpoint(flask_app)

    client.get(url_for('api.test_resource'))
    parser = RequestParamParser('test')
    assert parser.str() is None


def test_str_parsing(flask_app, client):

    with flask_app.test_request_context('/?test=1'):
        parser = RequestParamParser('test')
        assert parser.str() == '1'

    with flask_app.test_request_context('/?test=%s*#£asdasad'):
        parser = RequestParamParser('test')
        assert parser.str() == '%s*#£asdasad'


def test_int_parsing(flask_app, client):

    with flask_app.test_request_context('/?test=1'):
        parser = RequestParamParser('test')
        assert parser.int() == 1

    with flask_app.test_request_context('/?test=one'):
        parser = RequestParamParser('test')
        assert parser.int() is None

    with flask_app.test_request_context('/?test=0'):
        parser = RequestParamParser('test')
        assert parser.int() == 0


def test_int_parser_missing_param(flask_app, client):

    _build_endpoint(flask_app)

    client.get(url_for('api.test_resource'))
    parser = RequestParamParser('test')
    assert parser.int() is None


def test_date_parser_missing_param(flask_app, client):

    _build_endpoint(flask_app)

    client.get(url_for('api.test_resource'))
    parser = RequestParamParser('test')
    assert parser.date() is None


def test_date_parsing(flask_app, client):

    with flask_app.test_request_context('/?since=1'):
        parser = RequestParamParser('since')
        assert parser.date() is None

    with flask_app.test_request_context('/?since=2016-01-01'):
        parser = RequestParamParser('since')
        assert parser.date() == \
            datetime.datetime.strptime('2016-01-01', '%Y-%m-%d').date()


def test_iso8601_parsing(flask_app, client):

    with flask_app.test_request_context('/?since=1'):
        parser = RequestParamParser('since')
        assert parser.iso8601() is None

    with flask_app.test_request_context('/?since=2007-01-25T12:00:00Z'):
        parser = RequestParamParser('since')
        assert parser.iso8601() == iso8601.parse_date('2007-01-25T12:00:00Z')


def test_iso8601_parser_missing_param(flask_app, client):

    with flask_app.test_request_context('/'):
        parser = RequestParamParser('test')
        assert parser.iso8601() is None
