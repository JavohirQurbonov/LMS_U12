from django import forms

from courses.models import Module, Lesson


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ('title', 'description', 'order')
        labels = {'title': 'Sarlavha', 'description': 'Tavsif', 'order': 'Tartib'}
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('title', 'description', 'order')
        labels = {'title': 'Sarlavha', 'description': 'Tavsif', 'order': 'Tartib'}
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}
