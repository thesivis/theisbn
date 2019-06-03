#from __future__ import annotations
from theisbnapi.models import ISBN

from abc import ABC, abstractmethod
from django.db.models import Q
from bs4 import BeautifulSoup
import requests
import json
from django.core import serializers
from django.conf import settings
import datetime
import random
import os
import pytesseract
try:
    import Image
except ImportError:
    from PIL import Image
from subprocess import check_output

class Node(ABC):

    @abstractmethod
    def search(self, parametros):
        pass


class LocalNode(Node):

    def search(self, request) -> str:
        print(self.__class__.__name__)
        try:
            query = ISBN.objects.get(Q(isbn13=request['isbn'])| Q(isbn10=request['isbn']))
            fields = serializers.serialize('json',[query,])
            obj = json.loads(fields)
            return {"status":"ok",'type':self.__class__.__name__, "book": obj[0]['fields']}
        except ISBN.DoesNotExist:
            return {"status":"erro"}

class ISBNSearchNode(Node):

    def search(self, request) -> str:
        print(self.__class__.__name__)
        data = {
            'searchQuery': request['isbn'],
            'searchSubmit':''
        }
        headers = {
            'Host' : 'isbnsearch.org',
            'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language' : 'en-US,en;q=0.5',
            'Accept-Encoding' : 'gzip, deflate, br',
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Content-Length' : '39',
            'Referer': 'https://isbnsearch.org/',
            'Connection' : 'keep-alive',
            'Upgrade-Insecure-Requests' : '1',
        }
        #req = requests.post('https://isbnsearch.org/search',data = data, headers=headers)
        headers = {
            'Host' : 'isbnsearch.org',
            'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language' : 'en-US,en;q=0.5',
            'Accept-Encoding' : 'gzip, deflate, br',
            'Connection' : 'keep-alive',
            'Upgrade-Insecure-Requests' : '1',
        }
        req = requests.get('https://isbnsearch.org/isbn/'+request['isbn'],headers=headers)
        print('https://isbnsearch.org/isbn/'+request['isbn'])
        if req.status_code == 200:
            print('Requisição bem sucedida!')
            print(req.content)
            print('--------------------------------------------------------------------------')
            print(req.text)
            content = req.content
            soup = BeautifulSoup(content, 'html.parser')
            book = soup.find(name='div',attrs={"class":'bookinfo'})
            print(book)

        return {"status":"erro"}

class GoogleBookAPINode(Node):

    def search(self, request) -> str:
        print(self.__class__.__name__)
        url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + request['isbn']
        req = requests.get(url)
        if req.status_code == 200:
            content = req.content
            obj = json.loads(content)
            if(obj['totalItems'] > 0):
                book = obj['items'][0]['volumeInfo']
                livro = {}
                isbns = book['industryIdentifiers']

                isbn13 = ''
                isbn10 = ''
                if(len(isbns)>= 2):
                    for isbn in isbns:
                        if(isbn['type'] == 'ISBN_10'):
                            isbn10 = isbn['identifier']
                        elif(isbn['type'] == 'ISBN_13'):
                            isbn13 = isbn['identifier']

                livro['isbn13'] = isbn13
                livro['isbn10'] = isbn10
                livro['authors'] = ';'.join(book['authors'])
                livro['title'] = book['title']

                return {"status":"ok",'type':self.__class__.__name__, "book": livro}

        return {"status":"erro"}

class OpenLibraryAPINode(Node):

    def search(self, request) -> str:
        print(self.__class__.__name__)
        url = "https://openlibrary.org/api/books?bibkeys=ISBN:" + request['isbn']+"&format=json&jscmd=data"
        req = requests.get(url)
        if req.status_code == 200:
            content = req.content
            obj = json.loads(content)
            if(("ISBN:" + request['isbn']) in obj):
                book = obj[("ISBN:"+ request['isbn'])]
                livro = {}
                isbn13 = request['isbn']
                if(len(book['identifiers']['isbn_10']) > 0):
                    isbn10 = book['identifiers']['isbn_10'][0]

                livro['isbn13'] = isbn13
                livro['isbn10'] = isbn10
                livro['authors'] = ';'.join([a['name'] for a in book['authors']])
                livro['title'] = book['title']

                return {"status":"ok",'type':self.__class__.__name__, "book": livro}
                
        return {"status":"erro"}

class ISBNDBAPINode(Node):

    def search(self, request) -> str:
        print(self.__class__.__name__)
        h = {'Authorization': 'YOUR_REST_KEY'}
        url = "https://api2.isbndb.com/book/" + request['isbn']
        req = requests.get(url, headers=h)
        if req.status_code == 200:
            obj = req.json()
            livro = {}
            livro['isbn13'] = obj['isbn13']
            livro['isbn10'] = obj['isbn']
            livro['authors'] = ';'.join(obj['authors'])
            livro['title'] = obj['title']

            return {"status":"ok",'type':self.__class__.__name__, "book": livro}
                

        return {"status":"erro"}


class ISBNBrAPINode(Node):

    def search(self, request) -> str:
        print(self.__class__.__name__)

        s = requests.session()
        url = "http://www.isbn.bn.br/website/consulta/cadastro"
        h = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://www.isbn.bn.br/website/consulta/cadastro/filtrar',
            'Connection': 'keep-alive'
        }
        req = s.get(url)
        jsessionid = s.cookies.get_dict()['JSESSIONID']
        
        h = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept': 'image/webp,*/*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://www.isbn.bn.br/website/consulta/cadastro/filtrar',
            'Connection': 'keep-alive',
            'Cookie': 'JSESSIONID='+jsessionid
        }
        tentativa = 0
        while(tentativa < 10):
            data = datetime_object = datetime.datetime.now()
            tempo = int(datetime.datetime.timestamp(data)*1000)
            caminho = 'http://www.isbn.bn.br/website/jcaptcha?'+str(tempo)
            r = s.get(caminho, headers=h)
            path = str(random.getrandbits(128))+'.jpeg'
            open(path, 'wb').write(r.content)
            print('Resolving Captcha')
            captcha_text = resolve(path).replace(' ','')
            os.remove(path)
            print('Extracted Text',captcha_text)
            
            h = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': 'http://www.isbn.bn.br/website/consulta/cadastro/filtrar',
                'Connection': 'keep-alive',
                'Cookie': 'JSESSIONID='+jsessionid
            }
            url = 'http://www.isbn.bn.br/website/consulta/cadastro/filtrar'
            req = s.post(url, data={'campo':'1','valor':'9788573289206','imagemCaptcha':captcha_text},headers=h)
            soup = BeautifulSoup(req.text, 'html.parser')
            book = soup.find(name='span',attrs={"id":'imagemCaptcha.errors'})
            if(book == None):
                tentativa = 10
                div = soup.find(name='div',attrs={"class":'conteudo'})
                divs = div.findChildren("div", recursive=False)
                livro = {}
                for d in divs:
                    if(d.findChildren(name='strong', recursive=False)):
                        texto = d.text.strip().replace('ISBN ','').replace('Título ','').replace('Edição ','').replace('Tipo de Suporte ','').replace('Páginas ','').replace('Editor(a) ','').replace('Editor(a) ','').strip()
                        texto = d.text.strip()
                        
                        if('ISBN' in texto):
                            livro['isbn13'] = texto.replace('ISBN ','').strip()
                        if('Título' in texto):
                            livro['title'] = texto.replace('Título ','').strip()
                        if('Participações' in texto):
                            livro['authors'] = texto.replace('Participações ','').strip()
                        
                        livro['isbn10'] = ''

                return {"status":"ok",'type':self.__class__.__name__, "book": livro}

            tentativa = tentativa + 1
        
        return {"status":"erro"}

def resolve(path):
    samples = [100,200,300,400,500,600]
    chave = str(random.getrandbits(128))+'.jpeg'
    ranking = {}
    for sample in samples:
        check_output(['convert', path, '-resample', str(sample), chave])
        valor = pytesseract.image_to_string(Image.open(chave), lang='eng', config='--oem 3')
        if(valor not in ranking):
            ranking[valor] = 0
        ranking[valor] = ranking[valor] + 1
    valores = sorted(ranking.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)
    os.remove(chave)
    return valores[0][0]

def search(isbn):
    local = LocalNode()
    isbnSearch = ISBNSearchNode()
    googleBook = GoogleBookAPINode()
    openlibrary = OpenLibraryAPINode()
    isbndb = ISBNDBAPINode()
    isbnbr = ISBNBrAPINode()

    chain = [local, isbnbr, googleBook, openlibrary, isbndb, isbnSearch]

    for no in chain:
        ret = no.search(isbn)
        if(ret['status'] == 'ok'):
            if(ret['type'] != 'LocalNode'):
                if(settings.GRAVAR_LOCAL):
                    isbn = ISBN()
                    isbn.isbn13 = ret['book']['isbn13']
                    isbn.isbn10 = ret['book']['isbn10']
                    isbn.authors = ret['book']['authors']
                    isbn.title = ret['book']['title']
                    isbn.save()
            del ret['type']
            return ret

    return {"status":"erro"}