from rest_framework import serializers
from rest_framework.fields import empty


class SplitListField(serializers.ListField):
    def __init__(self, *args,  **kwargs):
        self.splitter = kwargs.pop('splitter', ',')
        super(SplitListField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        return super(SplitListField, self).to_representation(self.splitter.join(value))

    def get_value(self, dictionary):
        values = super(SplitListField, self).get_value(dictionary)
        if values is empty:
            return empty

        values_converted = []
        for value in values:
            values_converted += value.split(self.splitter)
        return values_converted
