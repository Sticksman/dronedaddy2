init python:
    import json
    import os

    open_file = renpy.file

    class MOOD(object):
        moods = ANGRY, DISSATISFIED, NEUTRAL, SATISFIED, HAPPY = range(-2, 2)

    class GENDER(object):
        identities = [MALE, FEMALE, FLUID, QUEER, OTHER] = range(5)

    class SEX(object):
        sexes = [MALE, FEMALE, INTERSEX, OTHER] = range(4)

    class ORIENTATION(object):
        orientations = [STRAIGHT, GAY, BI, ASEXUAL, OTHER] = range(5)

    class GENDER_SEX_RELATIONSHIP:
        relationships = [CIS, TRANS, OTHER] = range(2)

    class R_STATE(object):
        states = [HATE, DISLIKE, NEUTRAL, LIKE, LOVE] = range(-2, 2)

    # Do we need this?
    class MODIFIER(object):
        modifiers = [NEUTRAL, OPEN, COMMITTED] = range(3)


    # Character is reserved in renpy
    class DDCharacter(object):
        character_attrs = [
            'display_name',
            'description',
            'sex',
            'gender',
            'orientation',
            'gender_sex_relationship',
            'emotional_state',
            'relationship_thresholds'
        ]

        @staticmethod
        def init_hand_crafted_character(name, data_file_root, character_names):
            c = Character.init_character_from_file(name, data_file_root)
            relationships = Relationship.init_hand_crafted_relationship(name, data_file_root, character_names)
            c.relationships = relationships
            return c

        @staticmethod
        def load_state_from_file(name, data_file_root, attrs):
            data_file_path = os.path.join(root, name, 'character.json')

            serialized_state = {}
            with open_file(data_file_path) as f:
                serialized_state = json.loads(f.read())

            state = {}
            for attr in attrs:
                state[attr] = serialized_state.get(attr)
            return state

        @classmethod
        def init_character_from_file(cls, name, data_file_root):
           character_state = cls.load_state_from_file(name, data_file_root, cls.character_attrs)
           return cls(name, **character_state)

        def __init__(self, name, **kwargs):
            self.name = name
            self.relationships = []
            # This does magic, we define our list of attributes above, then we take a list of arguments by name
            # We use the list of attributes to pull the ones we want from the arguments
            # Then we validate it via validate
            # Before assigning it to ourselves
            for attr in self.character_attrs:
                value = kwargs.get(attr)
                value = self.validate(attr, value)
                setattr(self, attr, value)

        def validate(self, attr, value):
            # This checks to see if there exists a validate function for the attribute
            # For example if attr is display_name, then we'll try and forward to validate_display_name()
            # If no fn is found, then we just assume it's a noop and return true
            # Validate will return a value or raise an error if we need it
            if hasattr(self, 'validate_%s' % attr):
                fn = getattr(self, 'validate_%s' % attr)
                return fn(value)
            return value

        def validate_display_name(self, value):
            # If we're missing the value, then return the name
            if not value:
                return self.name
            return value

        def validate_sex(self, value):
            if value not in SEX.sexes:
                return SEX.OTHER
            return value

        def validate_gender(self, value):
            if value not in GENDER.identities:
                return GENDER.OTHER
            return value

        def validate_orientation(self, value):
            if value not in ORIENTATION.orientations:
                return ORIENTATION.OTHER
            return value

        def validate_gender_sex_relationship(self, value):
            if value in GENDER_SEX_RELATIONSHIP.relationships:
                return value
            # We always try and validate this after gender and sex so we should always be able to try and derive it
            # Only make assumptions about cisness and transness if we're certain by way of sex id and gender id
            elif self.sex in [SEX.MALE, sex.FEMALE] and self.gender in [GENDER.MALE, GENDER.FEMALE]:
                if self.sex == self.gender:
                    return GENDER_SEX_RELATIONSHIP.CIS
                else:
                    return GENDER_SEX_RELATIONSHIP.TRANS

            # Otherwise let's just say other
            return GENDER_SEX_RELATIONSHIP.OTHER

        def validate_relationship_thresholds(self, value):
            if not isinstance(value, dict) or len(value) < len(R_STATE.states):
                raise AttributeError("Relationship thresholds must be defined")

            for key in R_STATE.states():
                if key not in value:
                    raise AttributeError("Relationship thresholds are malformed. Make sure you've defined all of them.")

            return value



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
            file_name = '%s_%s.json' % (name, other_character_name)
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
                state=R_STATE.NEUTRAL,
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
            if value not in R_STATE.states:
                return R_STATE.NEUTRAL
            return value

        def validate_modifier(self, value):
            if value not in MODIFIER.modifiers:
                return MODIFIER.NEUTRAL
            return value

