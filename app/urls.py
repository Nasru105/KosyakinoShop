from django.contrib import admin
from django.urls import include, path
from app import settings
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls", namespace="main")),
    path("catalog/", include("goods.urls", namespace="catalog")),
    path("user/", include("users.urls", namespace="users")),
    path("cart/", include("carts.urls", namespace="carts")),
    path("orders/", include("orders.urls", namespace="orders")),
    # Запрос на ввод email
    path("password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    # Подтверждение отправки email
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    # Ссылка из письма
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    # Завершение процесса
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
