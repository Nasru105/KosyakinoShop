from django.test import TestCase
from users.models import User
from goods.models import Category, Product
from orders.models import Order, OrderItem


class OrderModelTest(TestCase):

    def test_create_order(self):
        user = User.objects.create(username="testuser")
        order = Order.objects.create(
            user=user,
            phone_number="79991112233",
            requires_delivery=True,
            delivery_address="Москва, ул. Пушкина",
            payment_on_get=True,
            is_paid=False,
            status="В обработке",
            comment="Тестовый заказ",
        )
        self.assertEqual(order.phone_number, "79991112233")
        self.assertEqual(order.display_id(), f"{order.id:05}")
        self.assertEqual(str(order), f"Заказ № {order.display_id()}")


class OrderItemModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.category = Category.objects.create(name="Категория1")
        self.product = Product.objects.create(
            name="Товар1",
            price=100.50,
            category=self.category,
            quantity=10,
            discount=5,
        )
        self.order = Order.objects.create(
            user=self.user,
            phone_number="79991112233",
        )

    def test_create_order_item(self):
        order_item = OrderItem.objects.create(
            order=self.order, product=self.product, name="Товар1", price=100.50, quantity=3
        )
        self.assertEqual(order_item.products_price(), 301.50)
        self.assertEqual(str(order_item), f"Товар {order_item.name} | Заказ №{self.order.display_id()}")

    def test_orderitem_queryset_total_price_and_quantity(self):
        OrderItem.objects.create(order=self.order, product=self.product, name="Товар1", price=100, quantity=2)
        OrderItem.objects.create(order=self.order, product=self.product, name="Товар2", price=50, quantity=1)

        order_items = OrderItem.objects.filter(order=self.order)
        self.assertEqual(order_items.total_quantity(), 3)
        self.assertEqual(order_items.total_price(), 100 * 2 + 50 * 1)
