from django.shortcuts import redirect

from typing import Any
from django.contrib import messages
from django.db import transaction
from django.forms import ValidationError
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail

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
        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name
        initial["phone_number"] = self.request.user.phone_number
        initial["delivery_address"] = self.request.user.address
        return initial

    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = self.request.user
                cart_items = Cart.objects.filter(user=user)

                if cart_items.exists():
                    order = Order.objects.create(
                        user=user,
                        phone_number=form.cleaned_data["phone_number"],
                        requires_delivery=form.cleaned_data["requires_delivery"] == "1",
                        delivery_address=form.cleaned_data["delivery_address"],
                        payment_on_get=form.cleaned_data["payment_on_get"] == "1",
                        comment=form.cleaned_data["comment"],
                    )

                order_items_details = []
                for cart_item in cart_items:
                    product = cart_item.product
                    name = product.name
                    price = product.sell_price()
                    quantity = cart_item.quantity

                    if product.quantity < quantity:
                        raise ValidationError(
                            f"Недостаточное количество товара {name} на складе. В наличии - {product.quantity}."
                        )

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        name=name,
                        price=price,
                        quantity=quantity,
                    )

                    product.quantity -= quantity
                    product.save()

                    order_items_details.append(f"{name} (x{quantity}) - {price} руб.")

                cart_items.delete()

                # Формируем текст письма
                subject = f"Новый заказ № {order.display_id()}"
                message = (
                    f"Пользователь: {user.get_full_name()} ({user.username})\n"
                    f"Email: {user.email}\n"
                    f"Телефон: +7 {phone_number_format(order.phone_number)}\n"
                    f"Адрес доставки: {order.delivery_address}\n"
                    f"Комментарий: {order.comment}\n\n"
                    f"Товары:\n" + "\n".join(order_items_details)
                )

                # Отправляем письмо
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=settings.ADMIN_EMAILS,
                    fail_silently=False,
                )

                messages.success(self.request, "Заказ оформлен!")
                return redirect("users:profile")

        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Оформление заказа"
        context["order"] = True
        return context
