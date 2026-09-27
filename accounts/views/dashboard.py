from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from courses.models import Course, Group, TestSubmission, AssignmentSubmission


@login_required
def dashboard(request):
    user = request.user

    if user.is_admin:
        return redirect('courses:manage_dashboard')

    if user.is_teacher and hasattr(user, 'teacher_profile'):
        return redirect('courses:manage_dashboard')

    student = getattr(user, 'student_profile', None)
    groups = student.groups.select_related('course') if student else Group.objects.none()
    enrolled_courses = Course.objects.filter(groups__in=groups).distinct() if student else Course.objects.none()
    test_results = TestSubmission.objects.filter(student=student).select_related('test')[:5] if student else []
    submissions = AssignmentSubmission.objects.filter(student=student).select_related('assignment')[:5] if student else []
    context = {
        'role': 'student',
        'student': student,
        'enrolled_courses': enrolled_courses,
        'all_courses': Course.objects.all()[:6],
        'test_results': test_results,
        'submissions': submissions,
    }
    return render(request, 'accounts/dashboard_student.html', context)
