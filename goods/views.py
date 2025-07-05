from typing import Any
from django.db.models import QuerySet
from django.db.models.base import Model as Model
from django.http import Http404
from django.shortcuts import get_list_or_404, render
from django.views.generic import DetailView, ListView

from goods.models import Categories, Products
from goods.utils import q_search


class CatalogView(ListView):
    model = Products
    template_name = "goods/catalog.html"
    context_object_name = "goods"
    paginate_by = 3

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        on_sale = self.request.GET.get("on_sale")
        order_by = self.request.GET.get("order_by")
        query = self.request.GET.get("q")

        # Получаем базовый QuerySet
        if category_slug == "all":
            goods = super().get_queryset()
        elif query:
            goods = q_search(query)
        else:
            goods = super().get_queryset().filter(category__slug=category_slug)
            if not goods.exists():
                raise Http404()  # Вызовет 404 если нет товаров

        # Применяем дополнительные фильтры
        if on_sale:
            goods = goods.filter(discount__gt=0)

        # Сортировка
        if order_by and order_by != "default":
            goods = goods.order_by(order_by)

        return goods  # .filter(quantity__gt=0)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Каталог товаров"
        context["category_slug"] = self.kwargs.get("category_slug")
        return context


class ProductView(DetailView):
    template_name = "goods/product.html"
    slug_url_kwarg = "product_slug"
    context_object_name = "product"

    def get_object(self, queryset: QuerySet[Any] | None = None) -> Model:
        product = Products.objects.get(slug=self.kwargs.get(self.slug_url_kwarg))
        return product

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_object().name
        return context
