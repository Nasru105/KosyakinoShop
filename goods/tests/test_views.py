from django.test import TestCase
from django.urls import reverse
from goods.models import Categories, Products


class CatalogViewTests(TestCase):

    def setUp(self):
        self.cat1 = Categories.objects.create(name="Категория1", slug="category-1")
        self.cat2 = Categories.objects.create(name="Категория2", slug="category-2")

        self.prod1 = Products.objects.create(
            name="Товар 1",
            category=self.cat1,
            price=100,
            quantity=5,
            discount=10,
            slug="product-1",
        )

        self.prod2 = Products.objects.create(
            name="Товар 2",
            category=self.cat2,
            price=200,
            quantity=2,
            discount=0,
            slug="product-2",
        )

    def test_catalog_all_products(self):
        url = reverse("catalog:catalog")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Товар 1")
        self.assertContains(response, "Товар 2")

    def test_catalog_filter_by_category(self):
        url = reverse("catalog:category", kwargs={"category_slug": "category-1"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Товар 1")
        self.assertNotContains(response, "Товар 2")

    def test_catalog_filter_by_on_sale(self):
        url = reverse("catalog:catalog")
        response = self.client.get(url, {"on_sale": "1"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Товар 1")
        self.assertNotContains(response, "Товар 2")

    def test_catalog_order_by_price(self):
        url = reverse("catalog:catalog")
        response = self.client.get(url, {"order_by": "price"})

        self.assertEqual(response.status_code, 200)
        goods = response.context["goods"]
        prices = list(goods.values_list("price", flat=True))
        self.assertEqual(prices, sorted(prices))

    def test_catalog_raises_404_for_nonexistent_category(self):
        url = reverse("catalog:category", kwargs={"category_slug": "unknown"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # def test_catalog_search(self):

    #     self.prod2 = Products.objects.create(
    #         name="test product",
    #         category=self.cat2,
    #         price=200,
    #         quantity=2,
    #         discount=0,
    #         slug="test-product",
    #     )

    #     url = reverse("catalog:search", query={"q": "товар"})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "Товар 1")
    #     self.assertContains(response, "Товар 2")
    #     self.assertNotContains(response, "test product")
