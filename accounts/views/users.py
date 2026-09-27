from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import admin_required
from accounts.forms import AdminUserCreationForm, UserEditForm
from accounts.models import CustomUser, Student, Teacher


@admin_required
def user_list(request):
    teachers = Teacher.objects.select_related('user').all()
    students = Student.objects.select_related('user').all()
    return render(request, 'accounts/user_list.html', {
        'teachers': teachers,
        'students': students,
        'teacher_count': teachers.count(),
        'student_count': students.count(),
    })


@admin_required
def user_create(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"{user.get_full_name() or user.username} ({user.get_role_display()}) qo'shildi.")
            return redirect('accounts:user_list')
    else:
        form = AdminUserCreationForm()
    return render(request, 'accounts/user_create.html', {'form': form})


@admin_required
def user_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Foydalanuvchi yangilandi.")
            return redirect('accounts:user_list')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'manage/form.html', {
        'form': form,
        'title': f"Tahrirlash: {user}",
        'cancel_url': reverse('accounts:user_list'),
    })


@admin_required
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        label = str(user)
        user.delete()
        messages.success(request, f"{label} o'chirildi.")
        return redirect('accounts:user_list')
    return render(request, 'manage/confirm_delete.html', {
        'object': user,
        'object_type': 'Foydalanuvchi',
        'cancel_url': reverse('accounts:user_list'),
    })
