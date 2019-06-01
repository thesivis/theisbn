#from __future__ import annotations
from theisbnapi.models import ISBN

from abc import ABC, abstractmethod
from django.db.models import Q
from bs4 import BeautifulSoup
import requests
import json
from django.core import serializers
from django.conf import settings

class Node(ABC):

    @abstractmethod
    def next(self, no : 'Node') -> 'Node':
        pass

    @abstractmethod
    def search(self, parametros):
        pass


class AbstractNode(Node):

    _next: Node = None

    def next(self, no: Node) -> Node:
        self._next = no
        return no

    @abstractmethod
    def search(self, request) -> str:
        if self._next:
            return self._next.search(request)

        return None


class LocalNode(AbstractNode):

    def search(self, request) -> str:
        try:
            query = ISBN.objects.get(Q(isbn13=request['isbn'])| Q(isbn10=request['isbn']))
            fields = serializers.serialize('json',[query,])
            obj = json.loads(fields)
            return {"status":"ok", "book": obj[0]['fields']}
        except ISBN.DoesNotExist:
            ret = super().search(request)
            if(ret['status'] == 'ok' and settings.GRAVAR_LOCAL):
                isbn = ISBN()
                isbn.isbn13 = ret['book']['isbn13']
                isbn.isbn10 = ret['book']['isbn10']
                isbn.authors = ret['book']['authors']
                isbn.title = ret['book']['title']
                isbn.save()
            return ret
        return {"status":"erro2"}

class ISBNSearchNode(AbstractNode):

    def search(self, request) -> str:
        print('chego2')
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
        else:
            ret = super().search(request)
            return ret
        return {"status":"erro3"}

class GoogleBookAPINode(AbstractNode):

    def search(self, request) -> str:
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

                return {"status":"ok", "book": livro}

        return {"status":"erro4"}

class OpenLibraryAPINode(AbstractNode):

    def search(self, request) -> str:
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

                return {"status":"ok", "book": livro}
                
        ret = super().search(request)
        return ret

class ISBNDBAPINode(AbstractNode):

    def search(self, request) -> str:
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

            return {"status":"ok", "book": livro}
                
        ret = super().search(request)
        return ret

class FimNode(AbstractNode):

    def search(self, request) -> str:
        return {"status":"erro"}


def chain():
    local = LocalNode()
    isbnSearch = ISBNSearchNode()
    googleBook = GoogleBookAPINode()
    openlibrary = OpenLibraryAPINode()
    isbndb = ISBNDBAPINode()
    fim = FimNode()
    local.next(googleBook).next(openlibrary).next(isbndb).next(isbnSearch).next(FimNode)

    return local