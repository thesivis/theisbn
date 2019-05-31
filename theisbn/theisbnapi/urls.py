from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^search/$', views.get_isbn, name='isbn-detail'),
]