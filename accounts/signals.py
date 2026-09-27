from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, Student, Teacher


@receiver(post_save, sender=CustomUser)
def ensure_role_profile(sender, instance, raw=False, **kwargs):
    # raw=True — obyekt "loaddata" orqali fixture'dan (data.json) yuklanmoqda.
    # Profillar fixture'ning o'zida bor. Signal ham profil yaratsa, fixture'dagi
    # profil bilan to'qnashib IntegrityError beradi.
    if raw:
        return
    if instance.is_superuser:
        return
    if instance.role == CustomUser.Role.TEACHER:
        Teacher.objects.get_or_create(user=instance)
    elif instance.role == CustomUser.Role.STUDENT:
        Student.objects.get_or_create(user=instance)
