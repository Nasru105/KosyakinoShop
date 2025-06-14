from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def index(request):
    context = {
        'title': 'Home',
        'content': 'главная страница магазина - Home'
    }
    return render(request, 'main/index.html', context)

def about(request):
    return HttpResponse('About page')
