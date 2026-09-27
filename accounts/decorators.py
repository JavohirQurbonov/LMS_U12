from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def _check(request, predicate):
    user = request.user
    if not user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    if not predicate(user):
        raise PermissionDenied
    return None


def admin_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        resp = _check(request, lambda u: u.is_admin)
        return resp or view(request, *args, **kwargs)
    return wrapper


def teacher_required(view):
    """Allow teachers and admins (admins can manage everything)."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        resp = _check(request, lambda u: u.is_admin or u.is_teacher)
        return resp or view(request, *args, **kwargs)
    return wrapper
