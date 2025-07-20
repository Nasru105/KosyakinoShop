from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from orders.models import Order, OrderItem


class OrderltemTabulareAdmin(admin.TabularInline):
    model = OrderItem
    fields = ["product_variant", "name", "price", "quantity"]
    search_fields = ["product_variant", "name"]
    extra = 0


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "name", "price", "quantity"]
    search_fields = ["order", "product_variant", "name"]


class OrderTabulareAdmin(admin.TabularInline):
    model = Order
    fields = ["order_link", "status", "requires_delivery", "payment_on_get", "created_timestamp"]
    readonly_fields = ["order_link", "created_timestamp"]
    extra = 0

    def order_link(self, obj):
        if obj.pk:
            url = reverse("admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
            return format_html('<a href="{}">Заказ № {}</a>', url, obj.display_id())
        return "-"

    order_link.short_description = "Ссылка на заказ"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "display_id",
        "user",
        # "requires_delivery",
        "status",
        "delivery_status",
        "payment_on_get",
        "created_timestamp",
        "comment",
    ]
    list_editable = ["status", "delivery_status"]
    search_fields = ["id", "user", "created_timestamp", "requires_delivery", "status"]
    list_filter = ["user", "created_timestamp", "requires_delivery", "delivery_status", "status"]
    readonly_fields = ["created_timestamp"]
    inlines = [OrderltemTabulareAdmin]
    ordering = ("-created_timestamp",)
