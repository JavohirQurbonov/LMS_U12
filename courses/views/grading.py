from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.decorators import teacher_required
from courses.forms import GradeForm
from courses.models import AssignmentSubmission, TestSubmission

from .helpers import manageable_courses


@teacher_required
def grading_list(request):
    courses = manageable_courses(request.user)
    submissions = (
        AssignmentSubmission.objects
        .filter(assignment__lesson__module__course__in=courses)
        .select_related('assignment__lesson', 'student__user')
        .order_by('is_checked', '-submitted_at')
    )
    return render(request, 'manage/grading_list.html', {
        'submissions': submissions,
        'pending': submissions.filter(is_checked=False).count(),
    })


@teacher_required
def grade_submission(request, pk):
    courses = manageable_courses(request.user)
    submission = get_object_or_404(
        AssignmentSubmission.objects
        .filter(assignment__lesson__module__course__in=courses)
        .select_related('assignment__lesson', 'student__user'),
        pk=pk,
    )
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.is_checked = True
            sub.graded_at = timezone.now()
            teacher = getattr(request.user, 'teacher_profile', None)
            if teacher:
                sub.graded_by = teacher
            sub.save()
            messages.success(request, "Topshiriq baholandi.")
            return redirect('courses:manage_grading')
    else:
        form = GradeForm(instance=submission)
    return render(request, 'manage/grade_submission.html', {
        'submission': submission, 'form': form,
        'cancel_url': reverse('courses:manage_grading'),
    })


@teacher_required
def test_results(request):
    courses = manageable_courses(request.user)
    results = (
        TestSubmission.objects
        .filter(test__lesson__module__course__in=courses)
        .select_related('test__lesson', 'student__user')
    )
    return render(request, 'manage/test_results.html', {'results': results})
