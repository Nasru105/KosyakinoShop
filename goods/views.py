from django.core.paginator import Paginator
from django.shortcuts import get_list_or_404, render

from goods.models import Products
from goods.utils import q_search


from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.core.paginator import Paginator
from goods.models import Products


def catalog(request, category_slug=None):
    page = request.GET.get("page", 1)
    on_sale = request.GET.get("on_sale", None)
    order_by = request.GET.get("order_by", None)
    query = request.GET.get("q", None)

    # Получаем базовый QuerySet
    if category_slug == "all":
        goods = Products.objects.all()
    elif query:
        goods = q_search(query)
        for good in goods:
            print(good)
    else:
        goods = Products.objects.filter(category__slug=category_slug)
        if not goods.exists():
            get_list_or_404(Products, category__slug=category_slug)  # Вызовет 404 если нет товаров

    # Применяем дополнительные фильтры
    if on_sale:
        goods = goods.filter(discount__gt=0)

    # Сортировка
    if order_by and order_by != "default":
        goods = goods.order_by(order_by)

    # Пагинация
    paginator = Paginator(goods, 3)
    current_page = paginator.page(page)

    context = {
        "title": "Kosyakino - Каталог",
        "goods": current_page,
        "category_slug": category_slug,
    }
    return render(request, "goods/catalog.html", context)


def product(request, product_slug):

    product = Products.objects.get(slug=product_slug)

    context = {
        "title": "Kosyakino - Каталог",
        "product": product,
    }
    return render(request, "goods/product.html", context)
