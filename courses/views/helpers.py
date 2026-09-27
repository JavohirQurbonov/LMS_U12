from django.core.exceptions import PermissionDenied

from courses.models import Course


def manageable_courses(user):
    if user.is_admin:
        return Course.objects.all()
    if user.is_teacher and hasattr(user, 'teacher_profile'):
        return user.teacher_profile.courses.all()
    return Course.objects.none()


def ensure_course_access(user, course):
    if user.is_admin:
        return
    if (user.is_teacher and hasattr(user, 'teacher_profile')
            and user.teacher_profile.courses.filter(pk=course.pk).exists()):
        return
    raise PermissionDenied
