from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from BandoodleBackEnd.permissions import AdvancedBandPermissions, IsInvitedUser
from bands.models import Band
from bands.serializers import BandSerializer, CreateUpdateBandSerializer

from rest_framework.viewsets import ModelViewSet


class BandViewSet(ModelViewSet):
    queryset = Band.objects.all()
    serializer_class = BandSerializer
    permission_classes = [IsAuthenticated, AdvancedBandPermissions]
    parser_classes = [JSONParser, MultiPartParser]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateUpdateBandSerializer
        else:
            return BandSerializer

    def destroy(self, request, *args, **kwargs):
        user = request.user
        try:
            band = Band.objects.get(pk=kwargs.get('pk'))
            band_users = band.users.all()
            if(user.is_superuser and user not in band_users) or len(band_users) <= 1:
                return super().destroy(request, args, kwargs)
            else:
                band.users.remove(user)
                band.save()
                return Response(status=status.HTTP_204_NO_CONTENT)


        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['PUT', 'PATCH'], permission_classes=[IsInvitedUser])
    def accept_invitation(self, request, pk=None):
        band = Band.objects.filter(pk=pk).first()
        if not band:
            return Response(data={'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, band)
        if request.user in band.users.all():
            return Response(data={'detail': 'Member already added'}, status=status.HTTP_400_BAD_REQUEST)
        band.invited_users.remove(request.user)
        band.users.add(request.user)
        band.save()
        data = BandSerializer(instance=band).data
        return Response(data=data, status=status.HTTP_200_OK)

    @list_route(methods=('GET',), permission_classes=(IsAuthenticated,))
    def invited_to_bands(self, request):
        invited_to = Band.objects.filter(invited_users=request.user).all()
        invited_to = BandSerializer(instance=invited_to, many=True).data
        return Response(data=invited_to, status=status.HTTP_200_OK)

