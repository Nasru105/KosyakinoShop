"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.views.decorators.cache import cache_page
from django.urls import path
from main import views

app_name = "main"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("about/", cache_page(60 * 5)(views.AboutView.as_view()), name="about"),
    path("contacts/", cache_page(60 * 5)(views.ContactsView.as_view()), name="contacts"),
    path("delivery/", cache_page(60 * 5)(views.DeliveryView.as_view()), name="delivery"),
    path("privacy-policy/", cache_page(60 * 5)(views.PrivacyPolicyView.as_view()), name="privacy_policy"),
]
