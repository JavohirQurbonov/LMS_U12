from django import forms

from accounts.models import Teacher
from courses.models import Course, Group


class CourseForm(forms.ModelForm):
    teachers = forms.ModelMultipleChoiceField(
        queryset=Teacher.objects.select_related('user').all(),
        required=False,
        label="O'qituvchilar",
        widget=forms.SelectMultiple(attrs={'size': 6}),
    )

    class Meta:
        model = Course
        fields = ('name', 'image', 'description', 'duration', 'price')
        labels = {
            'name': 'Nomi', 'image': 'Rasm', 'description': 'Tavsif',
            'duration': 'Davomiyligi (oy)', 'price': "Narxi (so'm)",
        }
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['teachers'].initial = self.instance.teachers.all()

    def save(self, commit=True):
        course = super().save(commit=commit)
        if commit:
            course.teachers.set(self.cleaned_data['teachers'])
        return course


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'course', 'teacher', 'students', 'start_date', 'end_date')
        labels = {
            'name': 'Guruh nomi', 'course': 'Kurs', 'teacher': "O'qituvchi",
            'students': "O'quvchilar", 'start_date': 'Boshlanish', 'end_date': 'Tugash',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'students': forms.SelectMultiple(attrs={'size': 8}),
        }
