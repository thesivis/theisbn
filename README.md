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

## Configurando o request

No arquivo theisbnapi/views.py crie o método para receber a requisição
```
from django.http import JsonResponse

def get_isbn(request):
    data = request.REQUEST
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

