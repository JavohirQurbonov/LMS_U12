from django.shortcuts import render

from accounts.decorators import teacher_required
from courses.models import AssignmentSubmission, Group, Lesson

from .helpers import manageable_courses


@teacher_required
def manage_dashboard(request):
    courses = manageable_courses(request.user).prefetch_related('modules')
    lesson_count = Lesson.objects.filter(module__course__in=courses).count()
    pending = AssignmentSubmission.objects.filter(
        assignment__lesson__module__course__in=courses, is_checked=False
    ).count()

    if request.user.is_admin:
        group_count = Group.objects.count()
    else:
        group_count = Group.objects.filter(course__in=courses).count()

    context = {
        'courses': courses,
        'course_count': courses.count(),
        'lesson_count': lesson_count,
        'pending': pending,
        'group_count': group_count,
    }
    return render(request, 'manage/dashboard.html', context)
