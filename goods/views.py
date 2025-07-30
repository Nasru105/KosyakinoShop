import json
from typing import Any
from django.db.models import QuerySet
from django.db.models.base import Model as Model
from django.http import Http404
from django.shortcuts import get_list_or_404, render
from django.views.generic import DetailView, ListView
from django.core.serializers.json import DjangoJSONEncoder

from goods.models import Category, Firm, Product, ProductVariant, Tag
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
        tags = self.request.GET.getlist("tags")  # список тегов
        firms = self.request.GET.getlist("firm")  # список производителей
        sizes = self.request.GET.getlist("size")  # список размеров

        if not category_slug and not query:
            goods = super().get_queryset()
        elif query:
            goods = q_search(query)
        else:
            goods = super().get_queryset().filter(category__slug=category_slug)

        if on_sale:
            goods = goods.filter(discount__gt=0)

        if tags:
            goods = goods.filter(tags__name__in=tags).distinct()

        if firms:
            goods = goods.filter(firm__name__in=firms).distinct()

        if sizes:
            goods = goods.filter(variants__size__in=sizes).distinct()

        if order_by and order_by != "default":
            goods = goods.order_by(order_by)
        else:
            goods = goods.order_by("-id")

        return goods  # .filter(quantity__gt=0)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Каталог товаров"
        context["category_slug"] = self.kwargs.get("category_slug")
        context["tags_query"] = self.request.GET.getlist("tags")  # список тегов
        context["firms_query"] = self.request.GET.getlist("firm")  # список производителей
        context["sizes_query"] = self.request.GET.getlist("size")  # список размеров

        # Фильтрация фирм по уникальным значениям и выбранной категории
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            firms = Product.objects.filter(category__slug=category_slug).values_list("firm__name", flat=True)
            sizes = ProductVariant.objects.filter(product__category__slug=category_slug).values_list("size", flat=True)
            tags = Tag.objects.filter(products__category__slug=category_slug).values_list("name", flat=True)
        else:
            firms = Product.objects.values_list("firm__name", flat=True)
            sizes = ProductVariant.objects.values_list("size", flat=True)
            tags = Tag.objects.values_list("name", flat=True)

        SIZE_ORDER = ["xs", "s", "m", "l", "xl", "2xl", "3xl", "4xl", "5xl"]
        context["firms"] = sorted(set(firms))
        context["sizes"] = sorted(
            set(sizes),
            key=lambda x: SIZE_ORDER.index(x.lower()) if x.lower() in SIZE_ORDER else float("-inf"),
        )
        context["tags"] = sorted(set(tags))

        return context


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

        variants_color_json = {}
        SIZE_ORDER = ["xs", "s", "m", "l", "xl", "2xl", "3xl", "4xl", "5xl"]
        size_index = {size: index for index, size in enumerate(SIZE_ORDER)}

        for v in variants:
            if v.color not in variants_color_json:
                variants_color_json[v.color] = []
            variants_color_json[v.color].append(
                {
                    "id": v.id,
                    "color": v.color,
                    "size": v.size,
                    "sku": v.sku,
                    "sell_price": str(v.sell_price()),
                    "price": str(v.price),
                    "discount": str(v.discount),
                    "quantity": v.quantity,
                    "description": v.description,
                }
            )

        # Сортировка размеров внутри каждого цвета
        for color, variant_list in variants_color_json.items():
            variants_color_json[color] = sorted(
                variant_list, key=lambda x: size_index.get(x["size"].lower(), -999)  # неизвестные — в конец
            )

        context.update(
            {
                "variants_color_json": variants_color_json,
                "variants_color_json_str": json.dumps(variants_color_json, cls=DjangoJSONEncoder),
                "title": product.name,
                "variant": variants.last(),
            }
        )

        return context
