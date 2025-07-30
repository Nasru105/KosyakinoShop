from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from goods.models import Category, Firm, ProductImage, Product, ProductVariant, Tag
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

    fields = ("link_to_change", "quantity", "color", "size", "price", "discount", "sku")

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
    search_fields = ["name", "sku", "description", "firm"]
    list_filter = ["category", "firm", "tags", "price", "discount"]
    inlines = [ProductImageInline, ProductVariantInline]
    save_on_top = True


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["sku", "link_to_product", "color", "size", "price", "discount", "quantity"]
    search_fields = ["product", "sku"]
    list_filter = ["size", "price", "discount"]
    fields = get_all_fields(ProductVariant, ["product", "sku", ("price", "discount")])

    save_as = True

    def link_to_product(self, obj):
        if obj.product_id:  # Используем product_id для проверки, чтобы избежать лишних запросов
            url = reverse(
                "admin:%s_%s_change" % (obj.product._meta.app_label, obj.product._meta.model_name),
                args=[obj.product_id],
            )
            return format_html('<a href="{}">{}</a>', url, str(obj.product.name))
        return "-"

    link_to_product.short_description = "Товар"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin): ...


@admin.register(Firm)
class FirmAdmin(admin.ModelAdmin): ...
