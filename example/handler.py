from arrested.handler import ResponseHandler


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
