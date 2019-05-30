from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^isbn/$', views.get_isbn, name='isbn-detail'),
]