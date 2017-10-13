from django.conf.urls import url, include

from cupper import views

app_name = 'cupper'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'login/$', views.do_login, name='login'),
    url(r'logout/$', views.logout, name='logout'),
    url(r'logged_out/$', views.logged_out, name='logged_out'),
    url(r'signup/$', views.signup, name='signup'),
    url(r'signup_success/$', views.signup_success, name='signup_success'),
    url(r'profile/$', views.profile, name='profile'),
    url(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'activation_success/$', views.activation_success),
    url(r'game/', views.game, name='game'),
    url(r'final_room/(?P<room_id>[0-9]+)/$', views.final_room, name='final_room'),
    url(r'room/(?P<room_id>[0-9]+)/$', views.room, name='room'),

]