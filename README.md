# theisbn

## Criando ambiente

```
virtualenv -p /usr/bin/python3.6 venv
source venv/bin/activate
pip install djangorestframework
pip install django
pip install django-cors-headers
pip install mysql-connector-python
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
            'read_default_file': './my.cnf',
        },
    }
}
...
```

Crie o arquivo my.cnf e coloque as configurações:
```
[client]
database = theisbn
user = <USUARIO>
password = <SENHA>
default-character-set = utf8
```
