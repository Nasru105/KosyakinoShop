from typing import Any
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View

from carts.mixins import CartMixin
from carts.models import Cart
from users.utils import get_user_carts
from goods.models import Product, ProductVariant


class CartAddView(CartMixin, View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        product = ProductVariant.objects.get(id=product_id)

        cart = self.get_cart(request, product_variant=product)

        if cart:
            cart.quantity += 1
            cart.save()
        else:
            Cart.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key if not request.user.is_authenticated else None,
                product_variant=product,
                quantity=1,
            )

        response_data = {
            "message": "Товар добавлен в корзину",
            "cart_items_html": self.render_cart(request),
        }

        return JsonResponse(response_data)


class CartChangeView(CartMixin, View):
    def post(self, request):
        cart_id = request.POST.get("cart_id")

        cart = self.get_cart(request, cart_id=cart_id)

        if cart:
            cart.quantity = request.POST.get("quantity")
            cart.save()

            quantity = cart.quantity

        response_data = {
            "message": "Количество изменено",
            "cart_items_html": self.render_cart(request),
            "quantity": quantity,
        }

        return JsonResponse(response_data)


class CartRemoveView(CartMixin, View):
    def post(self, request):
        cart_id = request.POST.get("cart_id")

        cart = self.get_cart(request, cart_id=cart_id)

        if cart:
            quantity = cart.quantity
            cart.delete()

        response_data = {
            "message": "Товар удален",
            "cart_items_html": self.render_cart(request),
            "quantity_deleted": quantity,
        }

        return JsonResponse(response_data)


def cart_remove(request):

    cart_id = request.POST.get("cart_id")

    cart = Cart.objects.get(id=cart_id)
    quantity = cart.quantity
    cart.delete()

    user_cart = get_user_carts(request)

    context: dict[str, Any] = {"carts": user_cart}

    # if referer page is create_order add key orders: True to context
    referer = request.META.get("HTTP_REFERER")
    if reverse("orders:create_order") in referer:
        context["order"] = True

    cart_items_html = render_to_string("carts/includes/included_cart.html", context, request=request)

    response_data = {
        "message": "Товар удален",
        "cart_items_html": cart_items_html,
        "quantity_deleted": quantity,
    }

    return JsonResponse(response_data)
