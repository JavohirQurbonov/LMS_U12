from django import forms

from courses.models import LessonVideo, LessonPresentation, LessonMaterial


class LessonVideoForm(forms.ModelForm):
    class Meta:
        model = LessonVideo
        fields = ('title', 'file', 'url', 'duration', 'order')
        labels = {
            'title': 'Sarlavha', 'file': 'Video fayl', 'url': 'YouTube/Vimeo havola',
            'duration': 'Davomiyligi (soniya)', 'order': 'Tartib',
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('file') and not cleaned.get('url'):
            raise forms.ValidationError("Video fayl yoki havola kiriting.")
        return cleaned


class LessonPresentationForm(forms.ModelForm):
    class Meta:
        model = LessonPresentation
        fields = ('title', 'file', 'order')
        labels = {'title': 'Sarlavha', 'file': 'Fayl', 'order': 'Tartib'}


class LessonMaterialForm(forms.ModelForm):
    class Meta:
        model = LessonMaterial
        fields = ('title', 'description', 'file', 'url', 'order')
        labels = {
            'title': 'Sarlavha', 'description': 'Tavsif',
            'file': 'Fayl', 'url': 'Havola', 'order': 'Tartib',
        }
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('file') and not cleaned.get('url'):
            raise forms.ValidationError("Fayl yoki havola kiriting.")
        return cleaned
