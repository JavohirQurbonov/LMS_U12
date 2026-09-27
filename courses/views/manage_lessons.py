from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import teacher_required
from courses.forms import LessonForm
from courses.models import Lesson, Module

from .helpers import ensure_course_access


@teacher_required
def lesson_manage(request, pk):
    lesson = get_object_or_404(Lesson.objects.select_related('module__course'), pk=pk)
    ensure_course_access(request.user, lesson.module.course)
    return render(request, 'manage/lesson_manage.html', {
        'lesson': lesson,
        'course': lesson.module.course,
        'videos': lesson.videos.all(),
        'presentations': lesson.presentations.all(),
        'materials': lesson.materials.all(),
        'tests': lesson.tests.all(),
        'assignments': lesson.assignments.all(),
    })


@teacher_required
def lesson_create(request, module_pk):
    module = get_object_or_404(Module.objects.select_related('course'), pk=module_pk)
    ensure_course_access(request.user, module.course)
    form = LessonForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        lesson = form.save(commit=False)
        lesson.module = module
        lesson.save()
        messages.success(request, "Dars qo'shildi.")
        return redirect('courses:manage_lesson', pk=lesson.pk)
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Yangi dars — {module.title}",
        'cancel_url': reverse('courses:manage_course_detail', args=[module.course_id]),
    })


@teacher_required
def lesson_edit(request, pk):
    lesson = get_object_or_404(Lesson.objects.select_related('module__course'), pk=pk)
    ensure_course_access(request.user, lesson.module.course)
    form = LessonForm(request.POST or None, instance=lesson)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Dars yangilandi.")
        return redirect('courses:manage_lesson', pk=lesson.pk)
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Tahrirlash: {lesson.title}",
        'cancel_url': reverse('courses:manage_lesson', args=[lesson.pk]),
    })


@teacher_required
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson.objects.select_related('module__course'), pk=pk)
    ensure_course_access(request.user, lesson.module.course)
    course_pk = lesson.module.course_id
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, "Dars o'chirildi.")
        return redirect('courses:manage_course_detail', pk=course_pk)
    return render(request, 'manage/confirm_delete.html', {
        'object': lesson, 'object_type': 'Dars',
        'cancel_url': reverse('courses:manage_course_detail', args=[course_pk]),
    })
