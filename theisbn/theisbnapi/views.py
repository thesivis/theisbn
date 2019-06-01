from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse, HttpResponse
import theisbnapi.chain_node.nodes as node
from django.core import serializers
from dicttoxml import dicttoxml


def get_isbn(request):
    data = request.GET
    if('isbn' in request.GET):
        data = node.chain().search(request.GET)
        if('format' in request.GET):
            if(request.GET['format'] == 'xml'):
                data = dicttoxml(data)
                data = data.decode()
                return HttpResponse(data, content_type='application/xml')
    return JsonResponse(data)


def get_isbns(request):
    data = request.GET
    if('isbns' in request.GET):
        parametros = {}
        for key in request.GET:
            if(key != 'isbns'):
                parametros[key] = request.GET[key]
            else:
                isbns = request.GET[key].split(',')
        response = []
        for isbn in isbns:
            parametros['isbn'] = isbn
            data = node.chain().search(parametros)
            data['isbn'] = isbn
            response.append(data)
        if('format' in request.GET):
            if(request.GET['format'] == 'xml'):
                response = dicttoxml(response)
                response = response.decode()
                return HttpResponse(response, content_type='application/xml')
        return JsonResponse(response, safe=False)
    return JsonResponse({"status","erro"})