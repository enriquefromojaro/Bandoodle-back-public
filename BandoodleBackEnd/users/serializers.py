from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.validators import ValidationError
from rest_framework.validators import UniqueForDateValidator

from users.models import Musician


class UserSerializer(ModelSerializer):
    avatar = serializers.ImageField(source='musician.avatar')

    class Meta:
        model = User
        fields = ['id', 'username', "first_name", "last_name", 'password', 'email', 'bands', 'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False
            },

        }
        depth = 1

    def create(self, validated_data):
        musician_data = validated_data.pop('musician', None)
        user = User.objects.create(**validated_data)
        user.set_password(validated_data.get('password'))
        self.create_or_update_profile(user, musician_data)
        user.save()
        return user

    def update(self, instance, validated_data):
        musician_data = validated_data.pop('musician', None)
        self.create_or_update_profile(instance, musician_data)
        return super(UserSerializer, self).update(instance, validated_data)

    def create_or_update_profile(self, user, musician_data):
        musician, created = Musician.objects.get_or_create(user=user, defaults=musician_data)
        if not created and musician_data is not None:
            super(UserSerializer, self).update(musician, musician_data)


class UserListSerializer(ModelSerializer):
    avatar = serializers.ImageField(source='musician.avatar')

    class Meta:
        model = User
        fields = ['id', 'username', "first_name", "last_name", 'email', 'avatar']
        read_only_fields = ['username', 'first_name', 'last_name', 'email', 'avatar']
