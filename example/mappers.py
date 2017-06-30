from kim import Mapper, field

from example.models import Planet, Character


class PlanetMapper(Mapper):

    __type__ = Planet

    id = field.Integer(read_only=True)
    name = field.String()
    description = field.String()
    created_at = field.DateTime(read_only=True)


class CharacterMapper(Mapper):

    __type__ = Character

    id = field.Integer(read_only=True)
    name = field.String()
    created_at = field.DateTime(read_only=True)
