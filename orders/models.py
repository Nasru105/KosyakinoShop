from django.db import models

from goods.models import Product, ProductVariant
from users.models import User


class OrderitemQuerySet(models.QuerySet):
    def total_price(self):
        return sum(cart.products_price() for cart in self)

    def total_quantity(self):
        if self:
            return sum(cart.quantity for cart in self)
        return 0


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает оплату"
        PAID = "paid", "Оплачено"
        FAILED = "failed", "Ошибка оплаты"

    class DeliveryStatus(models.TextChoices):
        PROCESSING = "processing", "В обработке"
        WAITING_PICKUP = "waiting_pickup", "Ожидает в пункте выдачи"
        DELIVERED = "delivered", "Товар доставлен"

    user = models.ForeignKey(
        to=User,
        on_delete=models.SET_DEFAULT,
        null=True,
        blank=True,
        default=None,
        verbose_name="Пользователь",
    )
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания заказа")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    requires_delivery = models.BooleanField(default=False, verbose_name="Требуется доставка")
    delivery_address = models.TextField(null=True, blank=True, verbose_name="Адрес доставки")
    payment_on_get = models.BooleanField(default=False, verbose_name="Оплата при получении")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус заказа",
    )
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PROCESSING,
        verbose_name="Статус доставки",
    )
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий")

    class Meta:
        db_table = "order"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ("-id",)

    def total_price(self):
        """
        Суммарная цена всех товаров в заказе.
        """
        return sum(item.products_price() for item in self.orderitem_set.all())

    def order_items_details(self):
        """
        Возвращает список строк с деталями товаров в заказе.
        """
        return [
            f"{item.name}: {item.quantity} * {item.price} ₽ = {item.products_price()} ₽"
            for item in self.orderitem_set.all()
        ]

    def __str__(self) -> str:
        return f"Заказ № {self.display_id()}"

    def display_id(self):
        return f"{self.id:05}"


class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, verbose_name="Заказ")
    product_variant = models.ForeignKey(
        to=ProductVariant, on_delete=models.SET_DEFAULT, default=None, null=True, blank=True, verbose_name="Продукт"
    )
    name = models.CharField(max_length=150, verbose_name="Название")
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата продажи")

    class Meta:
        db_table = "order_item"
        verbose_name = "Проданный товар"
        verbose_name_plural = "Проданные товары"
        ordering = ("-id",)

    objects = OrderitemQuerySet.as_manager()

    def products_price(self):
        return round(self.price * self.quantity, 2)

    def __str__(self) -> str:
        return f"Товар {self.name} | Заказ №{self.order.display_id()}"

    def product_link(self):
        return f"https:///kosyakino.up.railway.app/catalog/product/{self.product_variant.slug()}/"
