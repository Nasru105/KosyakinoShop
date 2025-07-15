from django.contrib import admin

from carts.models import Cart


class CartTabAdmin(admin.TabularInline):
    model = Cart
    fields = ["product_variant", "quantity", "created_timestamp"]
    search_fields = ["product_variant", "quantity", "created_timestamp"]
    readonly_fields = ["created_timestamp"]
    extra = 1


@admin.register(Cart)
class CartsAdmin(admin.ModelAdmin):
    list_display = ["user_display", "product_variant", "quantity", "created_timestamp"]
    search_fields = ["created_timestamp", "user", "product_variant"]
    list_filter = ["created_timestamp", "user", "product_variant"]

    def user_display(self, obj):
        if obj.user:
            return str(obj.user)
        return "Анонимный пользователь"
