from django.shortcuts import render


def catalog(request):

    context = {
        "title": "Kosyakino - Каталог",
        "goods": {},
    }
    return render(request, "goods/catalog.html", context)


def product(request):
    context = {}
    return render(request, "goods/product.html", context)
