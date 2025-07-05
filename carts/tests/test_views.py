from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from carts.models import Cart
from goods.models import Categories, Products

User = get_user_model()


class CartViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.category = Categories.objects.create(name="Test Category", slug="test-category")

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.product = Products.objects.create(
            name="Test Product",
            price=100,
            category=self.category,
            discount=10,
        )

    def test_cart_add_authenticated(self):
        self.client.login(username="testuser", password="testpass")

        response = self.client.post(
            reverse("carts:cart_add"),
            {"product_id": self.product.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Товар добавлен в корзину")

        # Проверяем, создалась ли корзина
        cart = Cart.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart.quantity, 1)

    def test_cart_add_anonymous(self):
        session = self.client.session
        session.save()

        response = self.client.post(
            reverse("carts:cart_add"),
            {"product_id": self.product.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)

        cart = Cart.objects.get(session_key=session.session_key, product=self.product)
        self.assertEqual(cart.quantity, 1)

    def test_cart_change_quantity(self):
        cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
        )
        self.client.login(username="testuser", password="testpass")

        response = self.client.post(
            reverse("carts:cart_change"),
            {
                "cart_id": cart.id,
                "quantity": 5,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)

        cart.refresh_from_db()
        self.assertEqual(int(cart.quantity), 5)

        data = response.json()
        self.assertIn("quantity", data)
        self.assertEqual(int(data["quantity"]), 5)

    def test_cart_remove_authenticated(self):
        cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=3,
        )
        self.client.login(username="testuser", password="testpass")

        response = self.client.post(
            reverse("carts:cart_remove"),
            {"cart_id": cart.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)

        # Проверяем, что корзины больше нет
        self.assertFalse(Cart.objects.filter(id=cart.id).exists())

        data = response.json()
        self.assertIn("quantity_deleted", data)
        self.assertEqual(data["quantity_deleted"], 3)
