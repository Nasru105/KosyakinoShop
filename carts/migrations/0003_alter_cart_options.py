# Generated by Django 5.2.4 on 2025-07-05 11:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0002_alter_cart_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart',
            options={'ordering': ('id',), 'verbose_name': 'Корзина', 'verbose_name_plural': 'Корзины'},
        ),
    ]
