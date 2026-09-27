from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import teacher_required
from courses.forms import LessonVideoForm, LessonPresentationForm, LessonMaterialForm
from courses.models import Lesson, LessonVideo, LessonPresentation, LessonMaterial

from .helpers import ensure_course_access


def _create(request, lesson_pk, form_class, label):
    lesson = get_object_or_404(Lesson.objects.select_related('module__course'), pk=lesson_pk)
    ensure_course_access(request.user, lesson.module.course)
    form = form_class(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.lesson = lesson
        obj.save()
        messages.success(request, f"{label} qo'shildi.")
        return redirect('courses:manage_lesson', pk=lesson.pk)
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Yangi {label.lower()} — {lesson.title}", 'multipart': True,
        'cancel_url': reverse('courses:manage_lesson', args=[lesson.pk]),
    })


def _edit(request, model, pk, form_class, label):
    obj = get_object_or_404(model.objects.select_related('lesson__module__course'), pk=pk)
    ensure_course_access(request.user, obj.lesson.module.course)
    form = form_class(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"{label} yangilandi.")
        return redirect('courses:manage_lesson', pk=obj.lesson_id)
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Tahrirlash: {obj.title}", 'multipart': True,
        'cancel_url': reverse('courses:manage_lesson', args=[obj.lesson_id]),
    })


def _delete(request, model, pk, label):
    obj = get_object_or_404(model.objects.select_related('lesson__module__course'), pk=pk)
    ensure_course_access(request.user, obj.lesson.module.course)
    lesson_pk = obj.lesson_id
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f"{label} o'chirildi.")
        return redirect('courses:manage_lesson', pk=lesson_pk)
    return render(request, 'manage/confirm_delete.html', {
        'object': obj, 'object_type': label,
        'cancel_url': reverse('courses:manage_lesson', args=[lesson_pk]),
    })


@teacher_required
def video_create(request, lesson_pk):
    return _create(request, lesson_pk, LessonVideoForm, 'Video')


@teacher_required
def video_edit(request, pk):
    return _edit(request, LessonVideo, pk, LessonVideoForm, 'Video')


@teacher_required
def video_delete(request, pk):
    return _delete(request, LessonVideo, pk, 'Video')


@teacher_required
def presentation_create(request, lesson_pk):
    return _create(request, lesson_pk, LessonPresentationForm, 'Prezentatsiya')


@teacher_required
def presentation_edit(request, pk):
    return _edit(request, LessonPresentation, pk, LessonPresentationForm, 'Prezentatsiya')


@teacher_required
def presentation_delete(request, pk):
    return _delete(request, LessonPresentation, pk, 'Prezentatsiya')


@teacher_required
def material_create(request, lesson_pk):
    return _create(request, lesson_pk, LessonMaterialForm, 'Material')


@teacher_required
def material_edit(request, pk):
    return _edit(request, LessonMaterial, pk, LessonMaterialForm, 'Material')


@teacher_required
def material_delete(request, pk):
    return _delete(request, LessonMaterial, pk, 'Material')
