from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bands.models import Band
from users.serializers import UserListSerializer
from events.serializers import ListEventSerializer


class BandSerializer(serializers.ModelSerializer):
    users = UserListSerializer(many=True)
    events = ListEventSerializer(many=True, read_only=True)

    class Meta:
        model = Band
        fields = ['id', 'name', 'genre', 'users', 'events', 'avatar']


def _set_instance_invited_users(instance, validated_data):
    '''

    :param instane: Band
    :param validated_data: dict
    :return: void
    '''
    invited = validated_data.get('invited_users', [])

    for elem in set(invited) - set(instance.users.all()):
        instance.invited_users.add(elem)
    if invited:
        del validated_data['invited_users']
    return instance, validated_data


class CreateUpdateBandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
        fields = ['id', 'name', 'genre', 'users', 'avatar', 'invited_users']
        extra_kwargs = {
            'invited_users': {
                'write_only': True,
                'required': False
            },
        }

    def update(self, instance, validated_data):
        instance, validated_data = _set_instance_invited_users(instance, validated_data)

        return super().update(instance, validated_data)

    def validate(self, attrs):
        invited = attrs.get('invited_users', [])
        users = attrs.get('users', [])
        common = [c for c in invited if c in users]
        if len(common) > 0:
            raise ValidationError({'user_conflict': 'users and invited_users cannot have common members'})
        return super(CreateUpdateBandSerializer,self).validate(attrs)
