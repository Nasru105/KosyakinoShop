from django.test import TestCase
from carts.models import Cart
from goods.models import Category, Product
from users.models import User


class CartModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", email="testuser@example.com")
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=100,
            discount=10,  # чтобы проверить sell_price
        )

    def test_cart_creation_with_user(self):
        cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=3,
        )
        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.product, self.product)
        self.assertEqual(cart.quantity, 3)

    def test_cart_creation_without_user(self):
        cart = Cart.objects.create(
            user=None,
            product=self.product,
            quantity=2,
            session_key="abcdef123456",
        )
        self.assertIsNone(cart.user)
        self.assertEqual(cart.session_key, "abcdef123456")

    def test_products_price(self):
        cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
        )
        # product.sell_price() = 100 - 10% = 90
        expected_price = round(90 * 2, 2)
        self.assertEqual(cart.products_price(), expected_price)

    def test_cart_str_with_user(self):
        cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=1,
        )
        expected_str = f"Корзина: {self.user.username} | Товар: {self.product.name} | Количество: {cart.quantity}"
        self.assertEqual(str(cart), expected_str)

    def test_cart_str_anonymous(self):
        cart = Cart.objects.create(
            user=None,
            product=self.product,
            quantity=1,
        )
        expected_str = f"Корзина: Анонимная | Товар: {self.product.name} | Количество: {cart.quantity}"
        self.assertEqual(str(cart), expected_str)

    def test_total_price_and_total_quantity_queryset(self):
        Cart.objects.create(user=self.user, product=self.product, quantity=2)
        Cart.objects.create(user=self.user, product=self.product, quantity=3)

        queryset = Cart.objects.filter(user=self.user)

        total_price = queryset.total_price()
        total_quantity = queryset.total_quantity()

        # sell_price = 100 - 10% = 90
        expected_price = round(2 * 90 + 3 * 90, 2)

        self.assertEqual(total_price, expected_price)
        self.assertEqual(total_quantity, 5)
