from django.test import TestCase
import pytest
from django.db import models


# Создаем временную тестовую модель для проверки
class DummyModel(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        app_label = "yourapp"  # нужно указать app_label для тестовых моделей


class TestGetFields(TestCase):

    def test_get_fields_ordered(self):
        from utils.utils import get_all_fields

        # Указываем желаемый порядок некоторых полей
        ordered_fields = ["username", "email"]
        fields = get_all_fields(DummyModel, ordered_fields)

        # Проверяем, что сначала идут поля из ordered_fields
        assert fields[0:2] == ["username", "email"]

        # Проверяем, что остальные поля тоже есть
        remaining_fields = set(fields[2:])
        expected_remaining = {"first_name", "last_name", "phone_number"}
        assert remaining_fields == expected_remaining

        # Убедимся, что id удалён
        assert "id" not in fields

    def test_get_fields_without_ordered_fields(self):
        from utils.utils import get_all_fields

        fields = get_all_fields(DummyModel, [])

        # Поле id должно быть удалено
        assert "id" not in fields

        # Все остальные поля должны остаться
        expected_fields = {"username", "email", "first_name", "last_name", "phone_number"}
        assert set(fields) == expected_fields


class TestPhoneNumberFormat(TestCase):
    def test_phone_number_format(self):
        from utils.utils import phone_number_format

        # Проверяем форматирование номера телефона
        assert phone_number_format("89123456789") == "(912) 345-67-89"
        assert phone_number_format("71234567890") == "(123) 456-78-90"
        assert phone_number_format("1234567890") == "1234567890"  # Неверный формат
        assert phone_number_format("") == ""  # Пустой номер
        assert phone_number_format(None) == ""  # None значение


class TestProductImagePath(TestCase):
    def test_product_image_path(self):
        from utils.utils import product_image_path

        class DummyProduct:
            name = "test_product"

        filename = "image.jpg"
        path = product_image_path(DummyProduct(), filename)

        # Проверяем, что путь сформирован правильно
        print(path)
        assert path == "goods_images/test_product/image.jpg"
