# Generated by Django 4.2.4 on 2023-09-21 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_billingaddress_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaddress',
            name='country',
            field=models.CharField(max_length=100),
        ),
    ]