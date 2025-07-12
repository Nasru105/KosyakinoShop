from django.contrib import admin
from goods.models import Categories, ProductImage, Products
from utils.utils import get_all_fields


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "quantity", "price", "discount", "sell_price"]
    list_editable = ["discount"]
    search_fields = ["name", "description"]
    list_filter = ["category", "quantity", "price", "discount", "firm", "sizes", "composition", "country"]
    fields = get_all_fields(
        Products,
        [
            "name",
            "category",
            ("price", "discount"),
        ],
    )
    inlines = [ProductImageInline]
