from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from goods.models import Categories


def index(request):

    context = {
        "title": "Kosyakino",
        "content": "Магазин Kosyakino",
    }

    return render(request, "main/index.html", context)


def about(request):
    context = {
        "title": "О нас",
        "content": "О нас",
        "text_on_page": "текст",
    }
    return render(request, "main/about.html", context)
