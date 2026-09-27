from django.db import models

from .user import CustomUser


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    avatar = models.ImageField(upload_to='students/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def phone(self):
        return self.user.phone

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return self.full_name


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    avatar = models.ImageField(upload_to='teachers/', blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True)
    experience = models.PositiveIntegerField(default=0, help_text="Tajriba (yillarda)")
    courses = models.ManyToManyField('courses.Course', related_name='teachers', blank=True)

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def phone(self):
        return self.user.phone

    def __str__(self):
        return self.full_name
