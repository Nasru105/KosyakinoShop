# Generated by Django 5.2.4 on 2025-07-13 14:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0001_initial'),
        ('goods', '0002_remove_product_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goods.productvariant', verbose_name='Товар'),
        ),
    ]
