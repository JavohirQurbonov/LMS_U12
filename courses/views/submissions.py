from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from courses.forms import AssignmentSubmissionForm
from courses.models import Assignment, AssignmentSubmission


@login_required
def assignment_submit(request, pk):
    assignment = get_object_or_404(Assignment.objects.select_related('lesson'), pk=pk)
    student = getattr(request.user, 'student_profile', None)
    if student is None:
        messages.error(request, "Faqat o'quvchilar topshiriq yuklay oladi.")
        return redirect('courses:lesson_detail', pk=assignment.lesson_id)

    existing = AssignmentSubmission.objects.filter(assignment=assignment, student=student).first()

    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=existing)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.student = student
            sub.submitted_at = timezone.now()
            sub.is_checked = False
            sub.save()
            messages.success(request, "Topshiriq yuborildi.")
            return redirect('courses:lesson_detail', pk=assignment.lesson_id)
    else:
        form = AssignmentSubmissionForm(instance=existing)

    return render(request, 'courses/assignment_submit.html', {
        'assignment': assignment, 'form': form, 'existing': existing,
    })
