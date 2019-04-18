from rest_framework import serializers
from base.util.misc_validators import validators


class UserPasswordLoginApiSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ValidateViaSMSApiSerializer(serializers.Serializer):
    pn = serializers.CharField(validators=[
        validators.get_validator('phone number'),
    ])


class ResetPasswordApiSerializer(serializers.Serializer):
    sid = serializers.CharField()
    pn = serializers.CharField()
    vcode = serializers.CharField()
    new_password = serializers.CharField()
