from django.shortcuts import render
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from BandoodleBackEnd.permissions import IsBandMemberOrAdmin
from timeOptions.models import TimeOption
from timeOptions.serializers import TimeOptionSerializer


class TimeOptionViewSet(ModelViewSet):
    queryset = TimeOption.objects.all()
    serializer_class = TimeOptionSerializer
    permission_classes = [IsAuthenticated, IsBandMemberOrAdmin]

    @detail_route(methods=['GET'], permission_classes=[IsAuthenticated])
    def toggle_vote(self, request, pk=None):
        time_option = self.get_object()
        user = request.user
        if user in time_option.voted_by.all():
            time_option.voted_by.remove(user)
        else:
            time_option.voted_by.add(user)
        time_option.save()
        data = TimeOptionSerializer(instance=time_option).data
        return Response(data=data)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return TimeOption.objects.all()
        else:
            return TimeOption.objects.filter(event__band__users=self.request.user)
