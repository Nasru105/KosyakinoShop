from django.urls import path
from users import views
from django.contrib.auth import views as auth_views

app_name = "user"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("registration/", views.UserRegistrationView.as_view(), name="registration"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("users-cart/", views.UserCartView.as_view(), name="users_cart"),
    path("logout/", views.logout, name="logout"),
]
