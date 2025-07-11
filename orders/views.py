from decimal import Decimal
from typing import Any
import uuid

from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.forms import ValidationError
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from yookassa import Payment

from app import settings
from carts.models import Cart
from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem
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
            }
        )
        return initial

    def form_valid(self, form):
        user = self.request.user
        cart_items = Cart.objects.select_related("product").filter(user=user)

        if not cart_items.exists():
            form.add_error(None, "Ваша корзина пуста.")
            return self.form_invalid(form)

        # Подготовка данных для заказа
        requires_delivery = form.cleaned_data["requires_delivery"] == "1"
        payment_on_get = form.cleaned_data["payment_on_get"] == "1"

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=user,
                    phone_number=form.cleaned_data["phone_number"],
                    requires_delivery=requires_delivery,
                    delivery_address=form.cleaned_data["delivery_address"],
                    payment_on_get=payment_on_get,
                    comment=form.cleaned_data["comment"],
                )

                order_items_details, total_price = self.create_order_items(order, cart_items)

                # Удаляем корзину
                cart_items.delete()

            # вне транзакции: почта и платёж

            self.send_order_email(order, user, order_items_details, total_price)

            if payment_on_get:
                messages.success(self.request, "Заказ успешно оформлен. Оплата при получении.")
                return redirect(self.success_url)

            confirmation_url = self.create_payment(order, total_price)

            messages.success(self.request, "Заказ оформлен. Перенаправляем на страницу оплаты.")
            return redirect(confirmation_url)

        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def create_order_items(self, order, cart_items):
        """
        Создаёт OrderItem и обновляет остатки товаров.
        Возвращает:
            - order_items_details (список строк)
            - total_price (Decimal)
        """
        order_items_details = []
        total_price = Decimal(0)

        products_to_update = []

        for item in cart_items:
            product = item.product
            quantity = item.quantity
            price = product.sell_price()

            if product.quantity < quantity:
                raise ValidationError(
                    f"Недостаточное количество товара '{product.name}'. В наличии: {product.quantity}."
                )

            OrderItem.objects.create(
                order=order,
                product=product,
                name=product.name,
                price=price,
                quantity=quantity,
            )

            product.quantity -= quantity
            products_to_update.append(product)

            total_price += price * quantity
            order_items_details.append(f"{product.name}: {price} x {quantity} = {price * quantity}₽")

        # bulk_update для оптимизации
        if products_to_update:

            for product in products_to_update:
                if product.quantity < 0:
                    product.quantity = 0
            from django.db import transaction

            transaction.on_commit(
                lambda: type(products_to_update[0]).objects.bulk_update(products_to_update, ["quantity"])
            )

        return order_items_details, total_price

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

    def send_order_email(self, order, user, order_items_details, total_price):
        """
        Отправляет email админу о новом заказе.
        """
        subject = f"Новый заказ №{order.display_id()}"
        message = (
            f"Пользователь: {user.get_full_name()} ({user.username})\n"
            f"Email: {user.email}\n"
            f"Телефон: +7 {phone_number_format(order.phone_number)}\n"
            f"Адрес доставки: {order.delivery_address}\n"
            f"Комментарий: {order.comment}\n"
            f"Товары:\n" + "\n".join(order_items_details) + "\n"
            f"Итого: {total_price}"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ADMINS_EMAILS,
            fail_silently=False,
        )

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Оформление заказа"
        context["order"] = True
        return context
