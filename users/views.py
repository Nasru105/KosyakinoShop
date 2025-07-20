from typing import Any
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from django.db.models import F, ExpressionWrapper, FloatField
from django.http import JsonResponse

from carts.models import Cart
from common.mixin import CacheMixin
from orders.models import Order, OrderItem
from users.forms import UserLoginForm, UserRegistrationForm, ProfileForm
from django.db.models import Sum

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from users.utils import get_user_orders


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = "users/login.html"
    success_url = reverse_lazy("main:index")

    def get_success_url(self):
        redirect_page = self.request.POST.get("next")
        if redirect_page and redirect_page != reverse("user:logout"):
            return str(redirect_page)
        return str(self.success_url)

    def form_valid(self, form):
        session_key = self.request.session.session_key

        user = form.get_user()
        if user:
            auth.login(self.request, user)
            if session_key:
                forgot_carts = Cart.objects.filter(user=user)
                if forgot_carts.exists():
                    forgot_carts.delete()
                Cart.objects.filter(session_key=session_key).update(user=user)

                messages.success(self.request, f"{user.username}, Вы вошли в аккаунт")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Kosyakino - Авторизация"
        return context


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("user:profile")

    def get_success_url(self):
        redirect_page = self.request.POST.get("next")
        if redirect_page and redirect_page != reverse("user:logout"):
            return str(redirect_page)
        return str(self.success_url)

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.instance

        if user:
            form.save()
            auth.login(self.request, user)

        if session_key:
            Cart.objects.filter(session_key=session_key).update(user=user)

        messages.success(
            self.request,
            f"{user.username}, Вы успешно зарегистрировались и вошли в аккаунт",
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Kosyakino - Регистрация"
        return context


class UserProfileView(LoginRequiredMixin, CacheMixin, UpdateView):
    form_class = ProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("user:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, f"Профиль успешно обновлен")
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Kosyakino - Профиль"

        orders = get_user_orders(self.request)[:5]
        # context["orders"] = self.set_cache_g(orders, f"orders_for_user_{self.request.user.pk}", 60)
        context["orders"] = orders
        return context

    def update_order_comment(request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if request.method == "POST":
            order.comment = request.POST.get("comment", "")
            order.save()
        return redirect(request.META.get("HTTP_REFERER", "/"))


class UserCartView(TemplateView):
    template_name = "users/user_cart.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Kosyakino - Корзина пользователя"
        return context


class UserOrdersView(TemplateView):
    template_name = "users/user_orders.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Kosyakino - Заказы пользователя"
        return context


@require_POST
@login_required
def update_order_comment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    comment = request.POST.get("comment", "").strip()

    order.comment = comment
    order.save()

    return JsonResponse({"status": "ok", "comment": comment})


@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, Вы вышли из аккаунта")
    auth.logout(request)
    return redirect(reverse("main:index"))
