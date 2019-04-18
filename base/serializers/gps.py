from rest_framework import serializers
from .fields.decimal import LatField, LngField


class GPSInfoSerializer(serializers.Serializer):

    lng = LngField()
    lat = LatField()


class OptionalGPSInfoSerializer(serializers.Serializer):
    lng = LngField(allow_null=True, default=None)
    lat = LatField(allow_null=True, default=None)
