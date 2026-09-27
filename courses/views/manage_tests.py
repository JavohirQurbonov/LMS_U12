from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import teacher_required
from courses.forms import TestForm, QuestionForm, AnswerOptionFormSet
from courses.models import Lesson, Test, Question

from .helpers import ensure_course_access


@teacher_required
def test_create(request, lesson_pk):
    lesson = get_object_or_404(Lesson.objects.select_related('module__course'), pk=lesson_pk)
    ensure_course_access(request.user, lesson.module.course)
    form = TestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        test = form.save(commit=False)
        test.lesson = lesson
        test.save()
        messages.success(request, "Test yaratildi. Endi savollar qo'shing.")
        return redirect('courses:manage_question', test_pk=test.pk)
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Yangi test — {lesson.title}",
        'cancel_url': reverse('courses:manage_lesson', args=[lesson.pk]),
    })


@teacher_required
def test_edit(request, pk):
    test = get_object_or_404(Test.objects.select_related('lesson__module__course'), pk=pk)
    ensure_course_access(request.user, test.lesson.module.course)
    form = TestForm(request.POST or None, instance=test)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Test yangilandi.")
        return redirect('courses:manage_question', test_pk=test.pk)
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Tahrirlash: {test.title}",
        'cancel_url': reverse('courses:manage_lesson', args=[test.lesson_id]),
    })


@teacher_required
def test_delete(request, pk):
    test = get_object_or_404(Test.objects.select_related('lesson__module__course'), pk=pk)
    ensure_course_access(request.user, test.lesson.module.course)
    lesson_pk = test.lesson_id
    if request.method == 'POST':
        test.delete()
        messages.success(request, "Test o'chirildi.")
        return redirect('courses:manage_lesson', pk=lesson_pk)
    return render(request, 'manage/confirm_delete.html', {
        'object': test, 'object_type': 'Test',
        'cancel_url': reverse('courses:manage_lesson', args=[lesson_pk]),
    })


@teacher_required
def question_manage(request, test_pk):
    test = get_object_or_404(
        Test.objects.select_related('lesson__module__course').prefetch_related('questions__options'),
        pk=test_pk,
    )
    ensure_course_access(request.user, test.lesson.module.course)
    return render(request, 'manage/question_list.html', {'test': test})


@teacher_required
def question_create(request, test_pk):
    test = get_object_or_404(Test.objects.select_related('lesson__module__course'), pk=test_pk)
    ensure_course_access(request.user, test.lesson.module.course)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = AnswerOptionFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.save()
            formset.instance = question
            formset.save()
            messages.success(request, "Savol qo'shildi.")
            return redirect('courses:manage_question', test_pk=test.pk)
    else:
        form = QuestionForm()
        formset = AnswerOptionFormSet()
    return render(request, 'manage/question_form.html', {
        'form': form, 'formset': formset, 'test': test, 'title': "Yangi savol",
    })


@teacher_required
def question_edit(request, pk):
    question = get_object_or_404(
        Question.objects.select_related('test__lesson__module__course'), pk=pk
    )
    ensure_course_access(request.user, question.test.lesson.module.course)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerOptionFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Savol yangilandi.")
            return redirect('courses:manage_question', test_pk=question.test_id)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerOptionFormSet(instance=question)
    return render(request, 'manage/question_form.html', {
        'form': form, 'formset': formset, 'test': question.test,
        'title': f"Savolni tahrirlash",
    })


@teacher_required
def question_delete(request, pk):
    question = get_object_or_404(
        Question.objects.select_related('test__lesson__module__course'), pk=pk
    )
    ensure_course_access(request.user, question.test.lesson.module.course)
    test_pk = question.test_id
    if request.method == 'POST':
        question.delete()
        messages.success(request, "Savol o'chirildi.")
        return redirect('courses:manage_question', test_pk=test_pk)
    return render(request, 'manage/confirm_delete.html', {
        'object': question, 'object_type': 'Savol',
        'cancel_url': reverse('courses:manage_question', args=[test_pk]),
    })
