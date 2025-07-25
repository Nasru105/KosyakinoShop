# Generated by Django 5.2.4 on 2025-07-16 09:39

import users.storages_backends
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, null=True, storage=users.storages_backends.UserImageStorage(), upload_to=users.storages_backends.UserImageStorage.image_path, verbose_name='Аватар'),
        ),
    ]
