from django.contrib import admin

# Register your models here.
from cupper.models import Profile, News

admin.site.register(Profile)
admin.site.register(News)
