from base import serializers
from ..choices import user_role_choice


class LoginApiSerializer(serializers.ApiSerializer):
    username = serializers.CharField()
    password = serializers.CharField()
    role = serializers.AliasChoiceField(user_role_choice)
