from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(default=1, help_text="Davomiyligi (oylarda)")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def lesson_count(self):
        from .structure import Lesson
        return Lesson.objects.filter(module__course=self).count()


class Group(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups')
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='groups')
    students = models.ManyToManyField('accounts.Student', related_name='groups', blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.course.name})"
