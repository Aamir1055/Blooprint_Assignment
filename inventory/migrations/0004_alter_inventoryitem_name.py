# Generated by Django 4.2.16 on 2024-10-09 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_alter_inventoryitem_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
