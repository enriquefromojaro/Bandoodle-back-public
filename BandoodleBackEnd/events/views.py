from rest_framework.viewsets import ModelViewSet
from events.models import Event
from events.serializers import EventSerializer
from rest_framework.permissions import IsAuthenticated
from BandoodleBackEnd.permissions import IsBandMemberOrAdmin


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsBandMemberOrAdmin]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Event.objects.all()
        else:
            return Event.objects.filter(band__users=self.request.user)
