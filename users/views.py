from email import message
from typing import Any
from urllib import request
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView
from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from django.db.models import F, ExpressionWrapper, FloatField

from carts.models import Cart
from common.mixin import CacheMixin
from orders.models import Order, OrderItem
from users.forms import UserLoginForm, UserRegistrationForm, ProfileForm
from django.db.models import Sum

from users.models import User
from utils.utils import get_fields


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

        orders = (
            Order.objects.filter(user=self.request.user)
            .prefetch_related(Prefetch("orderitem_set", queryset=OrderItem.objects.select_related("product")))
            .annotate(
                total_sum=Sum(
                    ExpressionWrapper(F("orderitem__price") * F("orderitem__quantity"), output_field=FloatField())
                )
            )
            .order_by("-id")
        )
        context["orders"] = self.set_g(orders, f"orders_for_user_{self.request.user.pk}", 60)
        return context


class UserCartView(TemplateView):
    template_name = "users/users_cart.html"


@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, Вы вышли из аккаунта")
    auth.logout(request)
    return redirect(reverse("main:index"))
