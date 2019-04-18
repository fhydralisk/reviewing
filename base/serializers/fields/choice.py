from rest_framework import serializers


class AliasChoiceField(serializers.ChoiceField):
    def __init__(self, read_field_choice, write_field_choice=None, allow_real_data=True, **kwargs):
        # type: (FieldChoice2, FieldChoice2, bool, dict) -> None

        if 'choices' in kwargs:
            raise ValueError("choice cannot exist in kwargs")

        self.allow_real_data = allow_real_data
        self.read_field_choice = read_field_choice
        if write_field_choice is None:
            self.write_field_choice = read_field_choice
        else:
            self.write_field_choice = write_field_choice

        super(AliasChoiceField, self).__init__(choices=read_field_choice.alias_choice.choice, **kwargs)

    def to_internal_value(self, data):
        if self.allow_null and data is None:
            return None

        elif self.allow_blank and not data:
            return data

        try:
            return self.write_field_choice.get_alias_real_data(data)
        except KeyError:
            if self.allow_real_data and data in self.write_field_choice.get_choices():
                return data
            self.fail('invalid_choice', input=data)

    def to_representation(self, value):
        if value is None:
            return value

        else:
            return self.read_field_choice.get_alias(value)
