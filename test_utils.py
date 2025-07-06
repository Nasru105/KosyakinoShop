from django.test import TestCase
import pytest
from django.db import models

from utils import get_fields


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
        # Указываем желаемый порядок некоторых полей
        ordered_fields = ["username", "email"]
        fields = get_fields(DummyModel, ordered_fields)

        # Проверяем, что сначала идут поля из ordered_fields
        assert fields[0:2] == ["username", "email"]

        # Проверяем, что остальные поля тоже есть
        remaining_fields = set(fields[2:])
        expected_remaining = {"first_name", "last_name", "phone_number"}
        assert remaining_fields == expected_remaining

        # Убедимся, что id удалён
        assert "id" not in fields

    def test_get_fields_without_ordered_fields(self):
        fields = get_fields(DummyModel, [])

        # Поле id должно быть удалено
        assert "id" not in fields

        # Все остальные поля должны остаться
        expected_fields = {"username", "email", "first_name", "last_name", "phone_number"}
        assert set(fields) == expected_fields
