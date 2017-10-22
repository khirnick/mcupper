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

    @staticmethod
    def get_best_users():
        """
        Получить 5 лучших игроков
        :return: объект игроков
        """

        users = Profile.objects.order_by('-score')[:5]

        return users


class News(models.Model):
    """
    Модель новости
    """

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @staticmethod
    def get_news_by_relevance():
        """
        Получить все новости в обратном порядке (по актуальности)
        :return: объект новостей
        """

        news = News.objects.order_by('-created_at')

        return news


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал при создании объекта User

    Добавляет доп. поле в модель
    :param sender: отправитель
    :param instance: объект пользователя
    :param created: если создан - True/False
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
