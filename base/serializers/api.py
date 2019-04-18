# coding=utf-8
from __future__ import unicode_literals
from rest_framework import serializers


class ReadonlySerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        raise AssertionError("%s does not update instances." % self.__class__.__name__)

    def create(self, validated_data):
        raise AssertionError("%s does not create instances." % self.__class__.__name__)


class ApiSerializer(ReadonlySerializer):
    pass
