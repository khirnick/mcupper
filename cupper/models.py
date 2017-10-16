from django.db import models
from django.contrib.auth.models import User, UserManager
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Модель профиля

    Расширение стандартной иодели пользователя
    Добавление поля 'score' - очки
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал при создании объекта User

    Добавляет доп. поле в модель
    :param sender: отправитель
    :param instance: объект пользователя
    :param created: если создан - True/False
    :return:
    """

    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Сигнал при изменении объекта User

    Сохраняет объект, которым расширен User
    :param sender: отправитель
    :param instance: объект пользователя
    """

    instance.profile.save()
