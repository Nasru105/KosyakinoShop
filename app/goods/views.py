from django.shortcuts import render

from goods.models import Products


def catalog(request):

    goods = Products.objects.all()

    context = {
        "title": "Kosyakino - Каталог",
        "goods": goods,
    }
    return render(request, "goods/catalog.html", context)


def product(request):
    context = {
        "title": "Kosyakino - Каталог",
    }
    return render(request, "goods/product.html", context)
