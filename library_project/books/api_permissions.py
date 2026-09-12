from urllib import request

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsLibrarianOrAdmin(BasePermission):
    """
    Custom permission to allow read-only access to regular members,
    while restricting write actions to Librarians, Admins, and Superusers.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always pass
        if request.user.is_superuser:
            return True

        # Read-only HTTP methods (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Write permissions (POST, PUT, DELETE) restricted to staff roles
        user_role = getattr(request.user.member_profile, 'role', None)
        return user_role in ['ADMIN', 'LIBRARIAN']



