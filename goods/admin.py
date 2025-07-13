from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from goods.models import Category, ProductImage, Product, ProductVariant
from utils.utils import get_all_fields


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    ordering = ("-sku",)
    readonly_fields = ("link_to_change",)

    fields = ("link_to_change", "color", "size", "price", "discount", "quantity", "sku")

    def link_to_change(self, obj):
        if obj.id:
            url = reverse("admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
            return format_html('<a href="{}">{}</a>', url, str(obj.sku))
        return "-"

    link_to_change.short_description = "Вариант"


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "price", "discount", "sell_price"]
    list_editable = ["discount"]
    search_fields = ["name", "description"]
    list_filter = ["category", "price", "discount"]
    fields = get_all_fields(Product, ["name", "category", ("price", "discount"), "description", "image", "slug"])
    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["sku", "link_to_change", "color", "size", "price", "discount", "quantity"]

    save_as = True

    def link_to_change(self, obj):
        if obj.id:
            url = reverse(
                "admin:%s_%s_change" % (obj.product._meta.app_label, obj.product._meta.model_name),
                args=[obj.product.pk],
            )
            return format_html('<a href="{}">{}</a>', url, str(obj.product.name))
        return "-"

    link_to_change.short_description = "Товар"
