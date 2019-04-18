import datetime
from rest_framework import serializers
from pytz import timezone


class TimestampField(serializers.Field):
    def to_representation(self, value):
        epoch = datetime.datetime(1970, 1, 1, tzinfo=timezone('UTC'))
        return int((value - epoch).total_seconds())

    def to_internal_value(self, data):
        # type: (int) -> datetime
        return datetime.datetime.utcfromtimestamp(float(data)).replace(tzinfo=timezone('UTC'))


class LocalDateTimeField(serializers.DateTimeField):

    def to_representation(self, value):
        from rest_framework.settings import api_settings
        output_format = getattr(self, 'format', api_settings.DATETIME_FORMAT)
        value = self.enforce_timezone(value)
        return value.strftime(output_format)
