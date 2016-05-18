from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^auth/$',views.auth,name='auth'),
    url(r'^home/$', views.home, name='home'),
    url(r'^send/$',views.send,name='send')
]