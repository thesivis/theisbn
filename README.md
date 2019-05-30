# theisbn

## Criando ambiente

virtualenv -p /usr/bin/python3.6 venv
source venv/bin/activate
pip install djangorestframework
pip install django
pip install django-cors-headers
pip install mysql-connector-python

## Criando a aplicação

django-admin startproject theisbn
cd theisbn/
python manage.py startapp theisbnapi
