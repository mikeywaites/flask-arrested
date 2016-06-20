from arrested import Api
from arrested.api import ListableResource, CreateableResource
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


class TestIndexApi(Api, ListableResource, CreateableResource):

    response_handler = TestResponseHandler
    request_handler = TestRequestHandler

    url = '/tests'
    endpoint_name = 'tests.index'
