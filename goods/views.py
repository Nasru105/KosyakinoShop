import json
from typing import Any
from django.db.models import QuerySet
from django.db.models.base import Model as Model
from django.http import Http404
from django.shortcuts import get_list_or_404, render
from django.views.generic import DetailView, ListView
from django.core.serializers.json import DjangoJSONEncoder

from goods.models import Category, Product
from goods.utils import q_search


class CatalogView(ListView):
    model = Product
    template_name = "goods/catalog.html"
    context_object_name = "goods"
    paginate_by = 6

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        on_sale = self.request.GET.get("on_sale")
        order_by = self.request.GET.get("order_by")
        query = self.request.GET.get("q")

        # Получаем базовый QuerySet
        if not category_slug and not query:
            goods = super().get_queryset()
        elif query:
            goods = q_search(query)
        else:
            goods = super().get_queryset().filter(category__slug=category_slug)

        # Применяем дополнительные фильтры
        if on_sale:
            goods = goods.filter(discount__gt=0)

        # Сортировка
        if order_by and order_by != "default":
            goods = goods.order_by(order_by)
        else:
            goods = goods.order_by("-id")

        return goods  # .filter(quantity__gt=0)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Каталог товаров"
        context["category_slug"] = self.kwargs.get("category_slug")
        return context


import json
from django.core.serializers.json import DjangoJSONEncoder


class ProductView(DetailView):
    template_name = "goods/product.html"
    slug_url_kwarg = "product_slug"
    context_object_name = "product"
    model = Product

    def get_object(self, queryset=None) -> Model:
        product = self.model.objects.get(slug=self.kwargs.get(self.slug_url_kwarg))
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        variants = product.variants.all()

        variants_json = [
            {
                "id": v.id,
                "color": v.color,
                "size": v.size,
                "sku": v.sku,
                "sell_price": str(v.sell_price()),
                "price": str(v.price),
                "discount": str(v.discount),
                "quantity": v.quantity,
            }
            for v in variants
        ]

        unique_colors = sorted(set(v.color for v in variants if v.color))

        # собрать уникальные размеры
        sizes_set = set(v.size for v in variants if v.size)
        SIZE_ORDER = ["xs", "s", "m", "l", "xl", "2xl", "3xl", "4xl", "5xl"]

        # сортировка по индексу в SIZE_ORDER
        unique_sizes = sorted(
            sizes_set, key=lambda x: SIZE_ORDER.index(x.lower()) if x.lower() in SIZE_ORDER else float("inf")
        )

        context.update(
            {
                "variants_json": json.dumps(variants_json, cls=DjangoJSONEncoder),
                "colors": unique_colors,
                "sizes": unique_sizes,
                "title": product.name,
                "variant": variants.first(),
            }
        )

        return context
