from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView

from goods.models import Category


class IndexView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Kosyakino"
        return context


class AboutView(TemplateView):
    template_name = "main/about.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Kosyakino - О нас"
        return context


class ContactsView(TemplateView):
    template_name = "main/contacts.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Kosyakino - Контакты"
        return context


class DeliveryView(TemplateView):
    template_name = "main/delivery.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Kosyakino - Доставка"
        return context


class PrivacyPolicyView(TemplateView):
    template_name = "main/privacy_policy.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Kosyakino - Политика конфиденциальности"
        return context
