from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from timeOptions.models import TimeOption
from users.serializers import UserListSerializer

class TimeOptionSerializer(ModelSerializer):
    # When created, an option must not be voted for any user and it will only be voted through the resource method.
    # So, we set the "voted_by" field as read_only
    voted_by = UserListSerializer(many=True, read_only=True)

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if end_time <= start_time:
            raise serializers.ValidationError({'end_time':"finish must occur after start"})
        return attrs

    class Meta:
        model = TimeOption
        fields = ['id', 'voted_by', 'date', 'start_time', 'end_time', 'event']
