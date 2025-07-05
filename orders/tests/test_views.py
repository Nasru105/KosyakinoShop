from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from carts.models import Cart
from goods.models import Categories, Products
from orders.models import Order, OrderItem

User = get_user_model()


class CreateOrderViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass", first_name="Иван", last_name="Иванов"
        )

        self.category1 = Categories.objects.create(name="Категория1")
        self.product1 = Products.objects.create(
            name="Товар1",
            price=100.50,
            category=self.category1,
            quantity=10,
            discount=5,
            description="Описание товара",
            image="test.jpg",
        )

        self.category2 = Categories.objects.create(name="Категория2")
        self.product2 = Products.objects.create(
            name="Товар2",
            price=200.75,
            category=self.category2,
            quantity=10,
            discount=10,
            description="Описание товара",
            image="test.jpg",
        )

        Cart.objects.create(
            user=self.user,
            product=self.product1,
            quantity=2,
        )

        Cart.objects.create(
            user=self.user,
            product=self.product2,
            quantity=4,
        )

        self.url = reverse("orders:create_order")

    def test_create_order_success(self):
        self.client.login(username="testuser", password="testpass")

        response = self.client.post(
            self.url,
            data={
                "first_name": "Иван",
                "last_name": "Иванов",
                "phone_number": "79991112233",
                "requires_delivery": "1",
                "delivery_address": "Москва, ул. Пушкина",
                "payment_on_get": "0",
                "comment": "Позвонить заранее",
            },
        )

        self.assertRedirects(response, reverse("users:profile"))

        order = Order.objects.get(user=self.user)
        self.assertEqual(order.phone_number, "79991112233")

        order_items = OrderItem.objects.filter(order=order)
        self.assertEqual(order_items.count(), 2)

        item1 = order_items.get(name="Товар1")
        item2 = order_items.get(name="Товар2")

        self.assertEqual(item1.quantity, 2)
        self.assertEqual(item2.quantity, 4)

        self.product1.refresh_from_db()
        self.assertEqual(self.product1.quantity, 8)

        self.product2.refresh_from_db()
        self.assertEqual(self.product2.quantity, 6)

        cart_count = Cart.objects.filter(user=self.user).count()
        self.assertEqual(cart_count, 0)

    def test_create_order_insufficient_quantity(self):
        self.client.login(username="testuser", password="testpass")

        # увеличиваем количество в корзине выше остатка
        Cart.objects.filter(user=self.user).update(quantity=20)

        response = self.client.post(
            self.url,
            data={
                "first_name": "Иван",
                "last_name": "Иванов",
                "phone_number": "79991112233",
                "requires_delivery": "1",
                "delivery_address": "Москва",
                "payment_on_get": "1",
                "comment": "Нет комментариев",
            },
        )

        self.assertEqual(response.status_code, 200)  # Проверяем, что нет редиректа

        # Проверяем, что форма есть в контексте и содержит ошибку
        form = response.context.get("form")
        self.assertIsNotNone(form)

        # Проверяем, что ошибка есть
        errors = [e.strip() for e in form.non_field_errors()]
        expected_error = "Недостаточное количество товара Товар1 на складе. В наличии - 10."
        # Заказ не создан
        self.assertTrue(any(expected_error in err for err in errors))
