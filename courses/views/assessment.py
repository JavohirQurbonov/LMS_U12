from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Test, TestAnswer, TestSubmission


@login_required
def test_take(request, pk):
    test = get_object_or_404(Test.objects.prefetch_related('questions__options'), pk=pk)
    return render(request, 'courses/test_take.html', {'test': test})


@login_required
def test_submit(request, pk):
    test = get_object_or_404(Test.objects.prefetch_related('questions__options'), pk=pk)
    student = getattr(request.user, 'student_profile', None)
    if request.method != 'POST' or student is None:
        return redirect('courses:test_take', pk=pk)

    questions = list(test.questions.all())
    total = len(questions)
    correct = 0

    submission = TestSubmission.objects.create(test=test, student=student, total_count=total)

    for question in questions:
        selected_ids = set(map(int, request.POST.getlist(f'question_{question.id}')))
        correct_ids = set(question.options.filter(is_correct=True).values_list('id', flat=True))
        is_correct = bool(correct_ids) and selected_ids == correct_ids
        if is_correct:
            correct += 1
        answer = TestAnswer.objects.create(submission=submission, question=question, is_correct=is_correct)
        if selected_ids:
            answer.selected_options.set(question.options.filter(id__in=selected_ids))

    score = (correct / total * 100) if total else 0
    submission.correct_count = correct
    submission.score = score
    submission.passed = score >= test.pass_score
    submission.save()

    return redirect('courses:test_result', pk=submission.pk)


@login_required
def test_result(request, pk):
    submission = get_object_or_404(TestSubmission.objects.select_related('test__lesson'), pk=pk)
    answers = submission.answers.select_related('question').prefetch_related(
        'question__options', 'selected_options'
    )
    return render(request, 'courses/test_result.html', {'submission': submission, 'answers': answers})
