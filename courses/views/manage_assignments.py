from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import teacher_required
from courses.forms import AssignmentForm
from courses.models import Assignment, Lesson

from .helpers import ensure_course_access


@teacher_required
def assignment_create(request, lesson_pk):
    lesson = get_object_or_404(Lesson.objects.select_related('module__course'), pk=lesson_pk)
    ensure_course_access(request.user, lesson.module.course)
    form = AssignmentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        assignment.lesson = lesson
        assignment.save()
        messages.success(request, "Topshiriq qo'shildi.")
        return redirect('courses:manage_lesson', pk=lesson.pk)
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Yangi topshiriq — {lesson.title}", 'multipart': True,
        'cancel_url': reverse('courses:manage_lesson', args=[lesson.pk]),
    })


@teacher_required
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment.objects.select_related('lesson__module__course'), pk=pk)
    ensure_course_access(request.user, assignment.lesson.module.course)
    form = AssignmentForm(request.POST or None, request.FILES or None, instance=assignment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Topshiriq yangilandi.")
        return redirect('courses:manage_lesson', pk=assignment.lesson_id)
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Tahrirlash: {assignment.title}", 'multipart': True,
        'cancel_url': reverse('courses:manage_lesson', args=[assignment.lesson_id]),
    })


@teacher_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment.objects.select_related('lesson__module__course'), pk=pk)
    ensure_course_access(request.user, assignment.lesson.module.course)
    lesson_pk = assignment.lesson_id
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, "Topshiriq o'chirildi.")
        return redirect('courses:manage_lesson', pk=lesson_pk)
    return render(request, 'manage/confirm_delete.html', {
        'object': assignment, 'object_type': 'Topshiriq',
        'cancel_url': reverse('courses:manage_lesson', args=[lesson_pk]),
    })
