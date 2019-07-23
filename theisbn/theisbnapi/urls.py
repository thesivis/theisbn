from . import views
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^search/$', views.get_isbn, name='isbn-detail'),
    url(r'^searchlist/$', views.get_isbns, name='isbns-details'),
    url(r'^searchview/$', views.searchview, name='searchview'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)