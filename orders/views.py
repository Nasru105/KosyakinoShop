from decimal import Decimal
import json
from typing import Any
import uuid

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import ValidationError
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import HttpResponse
from yookassa import Payment
from yookassa.domain.notification import WebhookNotificationFactory

from app import settings
from carts.models import Cart
from orders.models import Order, OrderItem
from orders.forms import CreateOrderForm
from utils.utils import phone_number_format


class CreateOrderView(LoginRequiredMixin, FormView):
    template_name = "orders/create_order.html"
    form_class = CreateOrderForm
    success_url = reverse_lazy("users:profile")

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {
                "first_name": self.request.user.first_name,
                "last_name": self.request.user.last_name,
                "phone_number": self.request.user.phone_number,
                "delivery_address": self.request.user.address,
                "requires_delivery": "0",  # Самовывоз
                "payment_on_get": "1",  # Наличными/картой при получении
            }
        )
        return initial

    def form_valid(self, form):
        user = self.request.user
        cart_items = Cart.objects.select_related("product_variant").filter(user=user)

        if not cart_items.exists():
            form.add_error(None, "Ваша корзина пуста.")
            return self.form_invalid(form)

        requires_delivery = form.cleaned_data["requires_delivery"] == "1"
        payment_on_get = form.cleaned_data["payment_on_get"] == "1"

        try:
            # Создаём заказ и order_items в транзакции
            with transaction.atomic():
                order = Order.objects.create(
                    user=user,
                    phone_number=form.cleaned_data["phone_number"],
                    requires_delivery=requires_delivery,
                    delivery_address=form.cleaned_data["delivery_address"],
                    payment_on_get=payment_on_get,
                    comment=form.cleaned_data["comment"],
                )

                self.create_order_items(order, cart_items)

            if payment_on_get:
                # Оплата при получении → корзину можно удалить
                cart_items.delete()
                messages.success(self.request, "Заказ успешно оформлен. Оплата при получении.")
                return redirect(self.success_url)

            try:
                confirmation_url = self.create_payment(order, order.total_price())
                cart_items.delete()  # удалить потом

                messages.success(self.request, "Заказ оформлен. Перенаправляем на страницу оплаты.")
                return redirect(confirmation_url)

            except Exception as e:
                # Ошибка при создании платежа
                # Удаляем заказ, чтобы не висел в базе
                order.delete()
                form.add_error(None, f"Ошибка при создании платежа: {e}")
                return self.form_invalid(form)

        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def create_order_items(self, order, cart_items):
        """
        Создаёт OrderItem и обновляет остатки товаров.
        """
        products_to_update = []

        for item in cart_items:
            product_variant = item.product_variant
            quantity = item.quantity
            price = product_variant.sell_price()

            if product_variant.quantity < quantity:
                raise ValidationError(
                    f"Недостаточное количество товара '{product_variant}'. В наличии: {product_variant.quantity}."
                )

            OrderItem.objects.create(
                order=order,
                product_variant=product_variant,
                name=product_variant,
                price=price,
                quantity=quantity,
            )

            product_variant.quantity -= quantity
            products_to_update.append(product_variant)

        # bulk_update
        if products_to_update:
            type(products_to_update[0]).objects.bulk_update(products_to_update, ["quantity"])

    def create_payment(self, order, total_price: Decimal):
        """
        Создаёт платёж через YooKassa и возвращает URL для редиректа.
        """
        payment = Payment.create(
            {
                "amount": {"value": str(total_price.quantize(Decimal("0.01"))), "currency": "RUB"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": self.request.build_absolute_uri(reverse("users:profile")),
                },
                "capture": True,
                "description": f"Заказ №{order.display_id()}",
                "metadata": {"order_id": str(order.id)},
            },
            uuid.uuid4(),
        )
        return payment.confirmation.confirmation_url

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Оформление заказа"
        context["order"] = True
        return context


@method_decorator(csrf_exempt, name="dispatch")  # Отключает CSRF-проверку для всех HTTP-методов этого класса
class YooKassaWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        data = json.loads(payload.decode())
        notification = WebhookNotificationFactory().create(data)

        if notification.event == "payment.succeeded":
            payment = notification.object
            order_id = payment.metadata.get("order_id")

            try:
                order = Order.objects.get(id=order_id)
                order.status = Order.STATUS_PAID
                order.save()

                # удаляем корзину пользователя
                Cart.objects.filter(user=order.user).delete()

                self.send_order_email(order)

            except Order.DoesNotExist:
                pass

        elif notification.event == "payment.canceled":
            # пользователь отказался платить
            payment = notification.object
            order_id = payment.metadata.get("order_id")

            try:
                order = Order.objects.get(id=order_id)
                order.status = Order.STATUS_FAILED
                order.save()

            except Order.DoesNotExist:
                pass

        return HttpResponse(status=200)

    def send_order_email(self, order):
        """
        Отправляет email админу о новом заказе.
        """
        subject = f"Новый заказ №{order.display_id()}"
        message = (
            f"Пользователь: {order.user.get_full_name()} ({order.user.username})\n"
            f"Email: {order.user.email}\n"
            f"Телефон: +7 {phone_number_format(order.phone_number)}\n"
            f"Адрес доставки: {order.delivery_address}\n"
            f"Комментарий: {order.comment}\n"
            f"Товары:\n" + "\n".join(order.order_items_details()) + f"\n\nИтого: {order.total_price()} ₽"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ADMINS_EMAILS,
            fail_silently=False,
        )
