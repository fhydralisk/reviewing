from base import serializers
from usersys.models import UserBase


class UserBaseSerializer(serializers.DynamicFieldsMixin, serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    registered_date = serializers.TimestampField(read_only=True)
    last_login = serializers.TimestampField(read_only=True)

    class Meta:
        model = UserBase
        fields = (
            'id',
            'internal_name',
            'password',
            'is_active',
            'role',
            'is_staff',
            'registered_date',
            'pn',
            'last_login',
        )

    def to_internal_value(self, data):
        if 'password' in data:
            user_model = self.Meta.model
            user_obj = user_model()
            user_obj.set_password(data['password'])
            data['password'] = user_obj.password
        return super(UserBaseSerializer, self).to_internal_value(data)


class UserChangingPasswordSerializer(UserBaseSerializer):
    old_password = serializers.CharField()

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + (
            'old_password',
        )


class UserDetailSerializer(serializers.ReadonlySerializer):
    user = UserBaseSerializer()


class UserPartialUpdateSerializer(serializers.ApiSerializer):
    update = UserChangingPasswordSerializer(fields=[
        'pn',
        'password',
        'old_password',
    ], partial=True)

    def validate(self, attrs):
        if attrs['update'].get('password') is not None and attrs['update'].get('old_password') is None:
            raise serializers.ValidationError(
                detail={'update.old_password': 'Required when password is filled.'}
            )
        return attrs
