from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import admin_required, teacher_required
from courses.forms import CourseForm, ModuleForm
from courses.models import Course, Module

from .helpers import ensure_course_access, manageable_courses


@teacher_required
def course_list_manage(request):
    courses = manageable_courses(request.user).prefetch_related('modules')
    return render(request, 'manage/course_list.html', {
        'courses': courses,
        'can_create': request.user.is_admin,
    })


@teacher_required
def course_manage(request, pk):
    course = get_object_or_404(
        Course.objects.prefetch_related('modules__lessons'), pk=pk
    )
    ensure_course_access(request.user, course)
    return render(request, 'manage/course_manage.html', {'course': course})


@admin_required
def course_create(request):
    form = CourseForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        course = form.save()
        messages.success(request, f"Kurs '{course.name}' yaratildi.")
        return redirect('courses:manage_course_detail', pk=course.pk)
    return render(request, 'manage/form.html', {
        'form': form, 'title': "Yangi kurs", 'multipart': True,
        'cancel_url': reverse('courses:manage_course_list'),
    })


@teacher_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    ensure_course_access(request.user, course)
    form = CourseForm(request.POST or None, request.FILES or None, instance=course)
    if not request.user.is_admin:
        form.fields.pop('teachers', None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Kurs yangilandi.")
        return redirect('courses:manage_course_detail', pk=course.pk)
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Tahrirlash: {course.name}", 'multipart': True,
        'cancel_url': reverse('courses:manage_course_detail', args=[course.pk]),
    })


@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, "Kurs o'chirildi.")
        return redirect('courses:manage_course_list')
    return render(request, 'manage/confirm_delete.html', {
        'object': course, 'object_type': 'Kurs',
        'cancel_url': reverse('courses:manage_course_list'),
    })


@teacher_required
def module_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    ensure_course_access(request.user, course)
    form = ModuleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        module = form.save(commit=False)
        module.course = course
        module.save()
        messages.success(request, "Modul qo'shildi.")
        return redirect('courses:manage_course_detail', pk=course.pk)
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Yangi modul — {course.name}",
        'cancel_url': reverse('courses:manage_course_detail', args=[course.pk]),
    })


@teacher_required
def module_edit(request, pk):
    module = get_object_or_404(Module.objects.select_related('course'), pk=pk)
    ensure_course_access(request.user, module.course)
    form = ModuleForm(request.POST or None, instance=module)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Modul yangilandi.")
        return redirect('courses:manage_course_detail', pk=module.course_id)
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Tahrirlash: {module.title}",
        'cancel_url': reverse('courses:manage_course_detail', args=[module.course_id]),
    })


@teacher_required
def module_delete(request, pk):
    module = get_object_or_404(Module.objects.select_related('course'), pk=pk)
    ensure_course_access(request.user, module.course)
    course_pk = module.course_id
    if request.method == 'POST':
        module.delete()
        messages.success(request, "Modul o'chirildi.")
        return redirect('courses:manage_course_detail', pk=course_pk)
    return render(request, 'manage/confirm_delete.html', {
        'object': module, 'object_type': 'Modul',
        'cancel_url': reverse('courses:manage_course_detail', args=[course_pk]),
    })
