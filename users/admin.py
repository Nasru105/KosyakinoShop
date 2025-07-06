from django.contrib import admin
from carts.admin import CartTabAdmin
from orders.admin import OrderTabulareAdmin
from users.models import User
from utils import get_fields


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    fields = get_fields(User, ["username", "first_name", "last_name", "email", "phone_number"])
    list_display = ["username", "first_name", "last_name", "email", "phone_number"]
    search_fields = ["username", "first_name", "last_name", "email", "phone_number"]

    inlines = [CartTabAdmin, OrderTabulareAdmin]
