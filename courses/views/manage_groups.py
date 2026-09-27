from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import admin_required
from courses.forms import GroupForm
from courses.models import Group


@admin_required
def group_list(request):
    groups = Group.objects.select_related('course', 'teacher__user').prefetch_related('students')
    return render(request, 'manage/group_list.html', {'groups': groups})


@admin_required
def group_create(request):
    form = GroupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Guruh yaratildi.")
        return redirect('courses:manage_group_list')
    return render(request, 'manage/form.html', {
        'form': form, 'title': "Yangi guruh",
        'cancel_url': reverse('courses:manage_group_list'),
    })


@admin_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    form = GroupForm(request.POST or None, instance=group)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Guruh yangilandi.")
        return redirect('courses:manage_group_list')
    return render(request, 'manage/form.html', {
        'form': form, 'title': f"Tahrirlash: {group.name}",
        'cancel_url': reverse('courses:manage_group_list'),
    })


@admin_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, "Guruh o'chirildi.")
        return redirect('courses:manage_group_list')
    return render(request, 'manage/confirm_delete.html', {
        'object': group, 'object_type': 'Guruh',
        'cancel_url': reverse('courses:manage_group_list'),
    })
