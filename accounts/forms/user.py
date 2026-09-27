from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import CustomUser, Student, Teacher

ROLE_CHOICES = [
    (CustomUser.Role.STUDENT, "O'quvchi"),
    (CustomUser.Role.TEACHER, "O'qituvchi"),
]


class AdminUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label="Ism")
    last_name = forms.CharField(max_length=150, label="Familiya")
    email = forms.EmailField(required=False, label="Email")
    phone = forms.CharField(max_length=20, required=False, label="Telefon")
    role = forms.ChoiceField(label="Rol", choices=ROLE_CHOICES)
    specialization = forms.CharField(max_length=100, required=False, label="Mutaxassislik (o'qituvchi)")
    experience = forms.IntegerField(min_value=0, required=False, label="Tajriba (yil)")
    birth_date = forms.DateField(required=False, label="Tug'ilgan sana (o'quvchi)",
                                 widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        user.email = self.cleaned_data.get('email', '')
        user.phone = self.cleaned_data.get('phone', '')
        if not commit:
            return user

        user.save()  # post_save signal creates the matching profile

        if user.role == CustomUser.Role.TEACHER:
            teacher = Teacher.objects.get(user=user)
            teacher.specialization = self.cleaned_data.get('specialization', '')
            teacher.experience = self.cleaned_data.get('experience') or 0
            teacher.save()
        elif user.role == CustomUser.Role.STUDENT:
            student = Student.objects.get(user=user)
            student.birth_date = self.cleaned_data.get('birth_date')
            student.save()

        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'is_active')
        labels = {
            'first_name': 'Ism', 'last_name': 'Familiya',
            'email': 'Email', 'phone': 'Telefon', 'is_active': 'Faol',
        }
