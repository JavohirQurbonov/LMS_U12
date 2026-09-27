from django import forms

from courses.models import Assignment, AssignmentSubmission


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'file', 'deadline', 'max_grade')
        labels = {
            'title': 'Sarlavha', 'description': 'Tavsif', 'file': 'Fayl',
            'deadline': 'Muddat', 'max_grade': 'Maksimal ball',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ('text', 'file')
        labels = {'text': 'Javob matni', 'file': 'Fayl'}
        widgets = {'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Javobingizni yozing...'})}


class GradeForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ('grade', 'comment')
        labels = {'grade': 'Ball', 'comment': 'Izoh'}
        widgets = {'comment': forms.Textarea(attrs={'rows': 3})}
