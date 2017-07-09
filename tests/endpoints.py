from arrested import (
    Endpoint, GetListMixin, GetObjectMixin,
    CreateMixin, PutObjectMixin, DeleteObjectMixin
)


def _get_character_objects():
    return [
        {
            'name': 'Hans Solo',
            'appears_in': [
                {
                    'name': "Return of the Jedi"
                }
            ]
        },
        {
            'name': 'Luke Skywalker',
            'appears_in': [
                {
                    'name': "Return of the Jedi"
                }
            ]
        }
    ]


def _get_planet_objects():
    return [
        {
            'name': 'Tatooine',
        },
        {
            'name': 'Dagobah',
        }
    ]


class CharactersEndpoint(Endpoint, GetListMixin, CreateMixin):

    name = 'list'
    many = True

    def get_objects(self):

        return _get_character_objects()


class CharacterEndpoint(Endpoint, GetObjectMixin, PutObjectMixin, DeleteObjectMixin):

    name = 'object'
    url = '/<string:obj_id>'

    def get_object(self):

        return _get_character_objects()[self.kwargs['obj_id']]


class PlanetsEndpoint(Endpoint, GetListMixin):

    name = 'list'

    def get_objects(self):

        return _get_planet_objects()
