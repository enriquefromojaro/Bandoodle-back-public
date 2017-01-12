from django.contrib.auth.models import User
from rest_framework import permissions

from bands.models import Band
from events.models import Event
from timeOptions.models import TimeOption


class IsBandMemberOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if isinstance(obj, Event):
            return request.user in obj.band.users.all()
        elif isinstance(obj, TimeOption):
            return request.user in obj.event.band.users.all()

        elif isinstance(obj, Band):
            return request.user in obj.users.all()
        # Increment the list of elif statements in case of incrementing the list of classes valid for this permission
        else:
            return False


class UserPermissions(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        else:
            return super(UserPermissions, self).has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if not super(UserPermissions, self).has_permission(request, view):
            return False
        if request.user.is_superuser or view.action == 'retrieve':
            return True
        else:
            return obj == request.user


class IsInvitedUser(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super(IsInvitedUser, self).has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if not super(IsInvitedUser, self).has_permission(request, view):
            return False
        return request.user in obj.invited_users.all()


class AdvancedBandPermissions(IsBandMemberOrAdmin):
    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return True

        if view.action == 'destroy':
            return request.user.is_superuser

        return super(AdvancedBandPermissions, self).has_object_permission(request, view, obj)
