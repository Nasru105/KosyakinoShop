from django.test import TestCase
from django.test import SimpleTestCase

from orders.forms import CreateOrderForm


class CreateOrderFormTest(SimpleTestCase):

    def test_valid_data(self):
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "phone_number": "79991112233",
            "requires_delivery": "1",
            "delivery_address": "Москва, ул. Пушкина",
            "payment_on_get": "0",
            "comment": "Позвонить заранее",
        }
        form = CreateOrderForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["phone_number"], "79991112233")

    def test_phone_with_letters(self):
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "phone_number": "79A91112233",
            "requires_delivery": "1",
            "delivery_address": "Москва",
            "payment_on_get": "0",
        }
        form = CreateOrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertIn("Номер должен содержать только цифры", form.errors["phone_number"])

    def test_phone_too_short(self):
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "phone_number": "7999",
            "requires_delivery": "1",
            "delivery_address": "Москва",
            "payment_on_get": "0",
        }
        form = CreateOrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertIn("Номер должен содержать 11 цифр", form.errors["phone_number"])

    def test_optional_fields_empty(self):
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "phone_number": "79991112233",
            "requires_delivery": "0",
            "payment_on_get": "1",
        }
        form = CreateOrderForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get("delivery_address", ""), "")
        self.assertEqual(form.cleaned_data.get("comment", ""), "")
