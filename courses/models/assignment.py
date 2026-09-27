from django.db import models

from .structure import Lesson


class Assignment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    max_grade = models.FloatField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='assignment_submissions')
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    is_checked = models.BooleanField(default=False)
    grade = models.FloatField(blank=True, null=True)
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    graded_by = models.ForeignKey('accounts.Teacher', on_delete=models.SET_NULL, blank=True, null=True, related_name='graded_submissions')

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student} — {self.assignment}"
