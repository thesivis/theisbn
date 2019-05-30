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
