from rest_framework import serializers
from events.models import Event
from timeOptions.serializers import TimeOptionSerializer


class EventSerializer(serializers.ModelSerializer):
    time_options = TimeOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'type', 'address', 'band', 'time_options', 'description']


class ListEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'type', 'address', 'band', 'description']
