# theisbn

## Criando ambiente

```
virtualenv -p /usr/bin/python3.6 venv
source venv/bin/activate
pip install djangorestframework
pip install django
pip install django-cors-headers
pip install mysql-connector-python
pip install mysqlclient
pip install bs4
pip install requests
pip install dicttoxml
```

## Criando a aplicação
```
django-admin startproject theisbn
cd theisbn/
python manage.py startapp theisbnapi
```

## Configurando o banco

No arquivo settings.py edite as linhas
```
...
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'my.cnf'),
        },
    }
}
...
```

Crie o arquivo <BASE_DIR>/my.cnf e coloque as configurações:
```
[client]
database = theisbn
host = 127.0.0.1
port = 3306
user = <USUARIO>
password = <SENHA>
default-character-set = utf8
```
Volte para o terminal e digite:
```
python manage.py migrate
```

## Configurando o settings.py

Na seção INSTALLED_APPS adicione:
```
'theisbnapi',
'rest_framework',
'corsheaders'
```
Já na seção de MIDDLEWARE adicione antes de CommonMiddleware:
```
'corsheaders.middleware.CorsMiddleware',
'django.middleware.common.CommonMiddleware',
```
E por fim ao final do arquivo adicione:
```
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False
```

## Configurando o request

No arquivo theisbnapi/views.py crie o método para receber a requisição
```
from django.http import JsonResponse

def get_isbn(request):
    data = {"status":"200"}
    return JsonResponse(data)
```

Crie o arquivo theisbnapi/urls.py e coloque:
```
from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^isbn/$', views.get_isbn, name='isbn-detail'),
]
```

No arquivo theisbn/urls.py configure a api:
```
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('theisbnapi.urls')),
    path('admin/', admin.site.urls),
]
```

## Criando o modelo

No arquivo theisbnapi/models.py crie os modelos do banco:

```
from django.db import models

# Create your models here.

class ISBN(models.Model):
    class Meta:
        db_table = "isbn"

    isbn13 = models.CharField(max_length=255)
    isbn10 = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    edition = models.CharField(max_length=255, null=True)
    binding = models.CharField(max_length=255, null=True)
    publisher = models.CharField(max_length=255, null=True)
    published = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255)
    
    def __str__(self):
        return self.title
```

Depois de criados os modelos no arquivo models.py, execute os comandos:
```
python manage.py makemigratios
python manage.py migrate
```
