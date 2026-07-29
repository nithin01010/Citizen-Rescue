from rest_framework import permissions
from accounts.models import User

class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object (or admin users) to edit it.
    Authenticated users are allowed read-only access.
    """
    def has_object_permission(self, request, view, obj):
        # Staff/Admin users have full access
        if request.user.is_staff or request.user.role == User.Role.ADMIN:
            return True
        
        # Read-only permissions are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Write permissions are only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user
