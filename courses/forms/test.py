from django import forms

from courses.models import Test, Question, AnswerOption


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ('title', 'description', 'pass_score', 'time_limit')
        labels = {
            'title': 'Sarlavha', 'description': 'Tavsif',
            'pass_score': "O'tish foizi (%)", 'time_limit': 'Vaqt chegarasi (daqiqa)',
        }
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', 'question_type', 'order')
        labels = {'text': 'Savol matni', 'question_type': 'Turi', 'order': 'Tartib'}
        widgets = {'text': forms.Textarea(attrs={'rows': 2})}


AnswerOptionFormSet = forms.inlineformset_factory(
    Question,
    AnswerOption,
    fields=('text', 'is_correct'),
    labels={'text': 'Variant', 'is_correct': "To'g'ri"},
    extra=4,
    can_delete=True,
)
