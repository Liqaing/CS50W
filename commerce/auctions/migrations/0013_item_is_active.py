# Generated by Django 4.2 on 2023-07-21 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_item_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]