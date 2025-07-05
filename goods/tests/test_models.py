from django.test import TestCase
from decimal import Decimal
from goods.models import Products, Categories
from django.core.exceptions import ValidationError


class ProductsModelTest(TestCase):

    def setUp(self):
        self.category = Categories.objects.create(name="Категория тест", slug="test-category")

    def test_str_method(self):
        product = Products.objects.create(
            name="Тестовый продукт",
            category=self.category,
            price=Decimal("100.00"),
            quantity=5,
            discount=Decimal("0.00"),
            slug="test-product",
        )
        self.assertEqual(str(product), "Тестовый продукт")

    def test_sell_price_no_discount(self):
        product = Products.objects.create(
            name="Товар без скидки",
            category=self.category,
            price=Decimal("150.00"),
            discount=Decimal("0.00"),
            quantity=10,
            slug="no-discount",
        )
        self.assertEqual(product.sell_price(), Decimal("150.00"))

    def test_sell_price_with_discount(self):
        product = Products.objects.create(
            name="Товар со скидкой",
            category=self.category,
            price=Decimal("200.00"),
            discount=Decimal("10.00"),  # 10%
            quantity=10,
            slug="discounted",
        )
        expected_price = Decimal("180.00")  # 200 - 10% = 180
        self.assertEqual(product.sell_price(), expected_price)

    def test_sell_price_rounding(self):
        product = Products.objects.create(
            name="Товар с округлением",
            category=self.category,
            price=Decimal("99.99"),
            discount=Decimal("5.00"),  # 5%
            quantity=10,
            slug="rounded-price",
        )
        expected_price = Decimal("94.99")  # 99.99 - 5% = 94.9905 → округляем до 94.99
        self.assertEqual(product.sell_price(), expected_price)

    def test_display_id_format(self):
        product = Products.objects.create(
            name="Новый товар", category=self.category, price=Decimal("50.00"), quantity=10, slug="new-product"
        )
        self.assertRegex(product.display_id(), r"^\d{5}$")

    def test_discount_cannot_exceed_100(self):
        product = Products(
            name="Слишком большая скидка",
            category=self.category,
            price=Decimal("100.00"),
            discount=Decimal("150.00"),  # 150% — должно быть недопустимо
            quantity=5,
            slug="too-much-discount",
        )
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_negative_discount_not_allowed(self):
        product = Products(
            name="Отрицательная скидка",
            category=self.category,
            price=Decimal("100.00"),
            discount=Decimal("-5.00"),
            quantity=5,
            slug="negative-discount",
        )
        with self.assertRaises(ValidationError):
            product.full_clean()
