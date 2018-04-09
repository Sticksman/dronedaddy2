import json
import os
import random

# For testing
try:
    import renpy
    open_file = renpy.file
except:
    open_file = open

class STATE(object):
    states = [HATE, DISLIKE, NEUTRAL, LIKE, LOVE] = range(-2, 2)


# Do we need this?
class MODIFIER(object):
    modifiers = [NEUTRAL, OPEN, COMMITTED] = range(3)


class Relationship(object):

    relationship_attrs = [
        'ship_name',
        'description',
        'score',
        'state',
        'modifier',
    ]

    # V2 write out the random relationship generator.
    # In order to do it, we need to write relationships to both characters at the same time
    # Modifier for OPEN needs to be recip

    @staticmethod
    def init_hand_crafted_relationship(name, data_file_root, character_names):
        ships = []
        for c_name in character_names:
            if name == c_name:
                # Skip if it's the same character
                continue
            ship = Relationship.init_relationship(name, c_name, data_file_root)
            ships.append(ship)
        return ships

    @staticmethod
    def init_blank_relationships(name, character_names);
        ships = []
        for c_name in character_names:
            if name == c_name:
                # Skip if it's the same character
                continue
            ship = Relationship.init_blank_relationship(name, c_name)
            ships.append(ship)
        return ships

    # Factor this method at some point
    @staticmethod
    def load_state_from_file(cls, name, other_character_name, data_file_root, attrs):
        file_name = '%s_%s.dat' % (name, other_character_name)
        file_path = os.path.join(data_file_root, 'relationships', file_name)

        serialized_state = {}
        with open_file(data_file_path) as f:
            serialized_state = json.loads(f.read())

        state = {}
        for attr in attrs:
            state[attr] = serialized_state.get(attr)
        return state

    @classmethod
    def init_relationship(cls, name, other_character_name, data_file_root):
        r_name = '%s_%s' % (name, other_character_name)
        state = cls.load_state_from_file(name, other_character_name, data_file_root, cls.relationship_attrs)
        return cls(r_name, **state)

    @classmethod
    def init_blank_relationship(name, other_character_name):
        r_name = '%s_%s' % (name, other_character_name)
        return cls(
            r_name,
            ship_name=r_name,
            description='A new relationship between %s and %s. Best watch it grow.' % (name, other_character_name),
            score=0,
            state=STATE.NEUTRAL,
            modifier=MODIFIER.NEUTRAL)

    def __init__(self, name, **kwargs):
        self.name = name
        for attr in self.relationship_attrs:
            value = kwargs.get(attr)
            self.validate(attr, value)

    def validate(self, attr, value):
        # This checks to see if there exists a validate function for the attribute
        # For example if attr is display_name, then we'll try and forward to validate_display_name()
        # If no fn is found, then we just assume it's a noop and return true
        # Validate will return a value or raise an error if we need it
        if hasattr(self, 'validate_%s' % attr):
            fn = getattr(self, 'validate_%s' % attr)
            return fn(value)
        return value

    def validate_ship_name(self, value):
        if not value:
            return self.name
        return value

    def validate_score(self, value):
        if not isinstance(value, int):
            return 0
        return value

    def validate_state(self, value):
        if value not in STATE.states:
            return STATE.NEUTRAL
        return value

    def validate_modifier(self, value):
        if value not in MODIFIER.modifiers:
            return MODIFIER.NEUTRAL
        return value
