from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Restricts access to users with specified roles.
    Usage: @role_required(['ADMIN', 'LIBRARIAN'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied

            # Superusers always pass
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check member profile role
            user_role = getattr(request.user.member_profile, 'role', None)
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            raise PermissionDenied("You do not have permission to access this page.")
        return _wrapped_view
    return decorator