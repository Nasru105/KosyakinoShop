from django.contrib import messages
from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import redirect, render

from carts.models import Cart
from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem

from django.contrib.auth.decorators import login_required

from typing import Any
from django.contrib import messages
from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from carts.models import Cart
from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem

from django.contrib.auth.decorators import login_required


class CreateOrderView(LoginRequiredMixin, FormView):
    template_name = "orders/create_order.html"
    form_class = CreateOrderForm
    success_url = reverse_lazy("users:profile")

    def get_initial(self):
        initial = super().get_initial()
        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name
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
                        requires_delivery=form.cleaned_data["requires_delivery"],
                        delivery_address=form.cleaned_data["delivery_address"],
                        payment_on_get=form.cleaned_data["payment_on_get"],
                    )

                for cart_item in cart_items:
                    product = cart_item.product
                    name = cart_item.product.name
                    price = cart_item.product.sell_price()
                    quantity = cart_item.quantity

                    if product.quantity < quantity:
                        raise ValidationError(
                            f"Недостаточное количество товара {name} на складе.\
                                                В наличии - {product.quantity}."
                        )

                    OrderItem.objects.create(order=order, product=product, name=name, price=price, quantity=quantity)

                    product.quantity -= quantity
                    product.save()

                cart_items.delete()

                messages.success(self.request, "Заказ оформлен!")
                return redirect("user:profile")
        except ValidationError as e:
            form.add_error(None, e)  # добавляем ошибку в форму
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Оформление заказа"
        context["order"] = True
        return context


@login_required
def create_order(request):
    if request.method == "POST":
        form = CreateOrderForm(data=request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = request.user
                    cart_items = Cart.objects.filter(user=user)

                    if cart_items.exists():
                        order = Order.objects.create(
                            user=user,
                            phone_number=form.cleaned_data["phone_number"],
                            requires_delivery=form.cleaned_data["requires_delivery"],
                            delivery_address=form.cleaned_data["delivery_address"],
                            payment_on_get=form.cleaned_data["payment_on_get"],
                        )

                    for cart_item in cart_items:
                        product = cart_item.product
                        name = cart_item.product.name
                        price = cart_item.product.sell_price()
                        quantity = cart_item.quantity

                        if product.quantity < quantity:
                            raise ValidationError(
                                f"Недостаточное количество товара {name} на складе.\
                                                  В наличии - {product.quantity}."
                            )

                        OrderItem.objects.create(
                            order=order, product=product, name=name, price=price, quantity=quantity
                        )

                        product.quantity -= quantity
                        product.save()

                    cart_items.delete()

                    messages.success(request, "Заказ оформлен!")
                    return redirect("user:profile")
            except ValidationError as e:
                form.add_error(None, e)  # добавляем ошибку в форму
                context = {"title": "Оформление заказа", "form": form, "order": True}
                return render(request, "orders/create_order.html", context=context)
        else:
            # форма невалидна (ошибки в requires_delivery и т.п.)
            context = {"title": "Оформление заказа", "form": form, "order": True}
            return render(request, "orders/create_order.html", context=context)
    else:
        initial = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }

        form = CreateOrderForm(initial=initial)

    context = {"title": "Оформление заказа", "form": form, "order": True}

    return render(request, "orders/create_order.html", context=context)
