from django.db import models

from .structure import Lesson


class LessonVideo(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='lessons/videos/', blank=True, null=True)
    url = models.URLField(blank=True, help_text="YouTube/Vimeo havolasi")
    duration = models.PositiveIntegerField(blank=True, null=True, help_text="Davomiyligi (soniya)")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class LessonPresentation(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='presentations')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='lessons/presentations/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class LessonMaterial(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='lessons/materials/', blank=True, null=True)
    url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title
