from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def index(request):
    context = {
        'title': 'Home',
        'content': 'Главная страница магазина - Home'
    }
    return render(request, 'main/index.html', context)

def about(request):
    context = {
        'title': 'О нас',
        'content': 'О нас',
        'text_on_page': 'текст'
    }
    return render(request, 'main/about.html', context)
