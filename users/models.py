from django.db import models
from django.contrib.auth.models import AbstractUser

from users.storages_backends import UserImageStorage


# Create your models here.
class User(AbstractUser):
    image = models.ImageField(
        upload_to=UserImageStorage.image_path,
        storage=UserImageStorage(),
        blank=True,
        null=True,
        verbose_name="Аватар",
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name="Номер телефона")
    email = models.EmailField(unique=True, verbose_name="Email")
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name="Адрес")

    class Meta:
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("-id",)

    def __str__(self):
        return self.username
