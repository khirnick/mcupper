from django.conf.urls import url, include

from cupper import views

urlpatterns = [
    url(r'signup/$', views.signup),
    url(r'signup_succes/$', views.signup_success),
    url(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate')
]