from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='tasks')
    correct_answer = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    @staticmethod
    def get_random_task():
        tasks = Task.objects.all()
        first_index = tasks.first().pk
        last_index = tasks.last().pk

        from random import randint
        random_index = randint(first_index, last_index)

        return tasks.get(pk=random_index)
