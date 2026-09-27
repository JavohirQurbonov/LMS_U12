from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from courses.models import Course, Lesson, TestSubmission, AssignmentSubmission


def _get_student(request):
    return getattr(request.user, 'student_profile', None)


@login_required
def course_list(request):
    courses = Course.objects.prefetch_related('modules').all()
    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(
        Course.objects.prefetch_related(
            Prefetch('modules__lessons', queryset=Lesson.objects.all())
        ),
        pk=pk,
    )
    return render(request, 'courses/course_detail.html', {'course': course})


@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson.objects.select_related('module__course'), pk=pk)
    student = _get_student(request)

    tests = lesson.tests.prefetch_related('questions')
    if student:
        passed_test_ids = set(
            TestSubmission.objects.filter(student=student, test__in=tests, passed=True)
            .values_list('test_id', flat=True)
        )
        submissions = {
            s.assignment_id: s
            for s in AssignmentSubmission.objects.filter(student=student, assignment__lesson=lesson)
        }
    else:
        passed_test_ids = set()
        submissions = {}

    context = {
        'lesson': lesson,
        'course': lesson.module.course,
        'videos': lesson.videos.all(),
        'presentations': lesson.presentations.all(),
        'materials': lesson.materials.all(),
        'tests': tests,
        'assignments': lesson.assignments.all(),
        'passed_test_ids': passed_test_ids,
        'submissions': submissions,
    }
    return render(request, 'courses/lesson_detail.html', context)
