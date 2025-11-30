from rest_framework.permissions import BasePermission


class IsBoardOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        account = request.user.account
        return obj.owner == account or obj.members.filter(id=account.id).exists()


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        account = request.user.account
        return obj.owner == account
