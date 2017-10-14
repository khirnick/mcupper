from django.conf.urls import url

from game import views


app_name = 'game'

urlpatterns = [
    url(r'^$', views.game, name='game'),
    url(r'final_room/(?P<room_id>[0-9]+)/$', views.final_room, name='final_room'),
    url(r'room/(?P<room_id>[0-9]+)/$', views.room, name='room'),
]