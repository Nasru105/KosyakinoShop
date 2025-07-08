from decimal import ROUND_HALF_UP, Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from utils.utils import product_image_path


class Categories(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name="URL")

    class Meta:
        db_table = "category"
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("id",)

    def __str__(self):
        return self.name


class Products(models.Model):
    id: int
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    category = models.ForeignKey(to=Categories, on_delete=models.CASCADE, verbose_name="Категория")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    image = models.ImageField(upload_to=product_image_path, blank=True, null=True, verbose_name="Изображение")
    price = models.DecimalField(
        default=Decimal("0.00"),
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена",
    )
    discount = models.DecimalField(
        default=Decimal("0.00"),
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Скидка (%)",
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name="URL")

    class Meta:
        db_table = "product"
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ("id",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:product", kwargs={"product_slug": self.slug})

    def display_id(self):
        return f"{self.id:05}"

    def sell_price(self):
        if self.discount:
            discount_amount = self.price * self.discount / Decimal("100")
            discounted_price = self.price - discount_amount
            # округлим до 2 знаков в сторону ближайшего
            return discounted_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return self.price


class ProductImage(models.Model):

    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_image_path, verbose_name="Изображение")

    class Meta:
        db_table = "product_image"
        verbose_name = "Изображение продукта"
        verbose_name_plural = "Изображения продуктов"
        ordering = ("id",)

    def __str__(self):
        return f"{self.product.name}"
