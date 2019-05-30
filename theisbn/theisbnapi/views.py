from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
import theisbnapi.chain_node.nodes as node

def get_isbn(request):
    data = request.GET
    if('isbn' in request.GET):
        data = node.chain().search(request.GET['isbn'])
    return JsonResponse(data)