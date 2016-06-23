from arrested import Api
from arrested.api import BaseListableResource, BaseCreateableResource
from arrested.handlers import Handler


class TestResponseHandler(Handler):

    def handle(self, data):
        return data


class TestRequestHandler(Handler):

    def handle(self, data):
        return data


class TestResource(Api):

    url = '/test'
    endpoint_name = 'test_resource'

    def get(self, *args, **kwargs):

        return ''


class TestIndexApi(Api, BaseListableResource, BaseCreateableResource):

    response_handler = TestResponseHandler
    request_handler = TestRequestHandler

    url = '/tests'
    endpoint_name = 'tests.index'


class MockUser(object):

    def __init__(self, id='1', username=None, email=None, is_admin=False):

        self.id = id
        self.username = username
        self.email = email
        self.is_admin = is_admin
