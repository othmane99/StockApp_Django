# Generated by Django 4.2.11 on 2024-05-22 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BeyondComV2', '0006_produit_creation_date_produit_is_warranty_valid_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produit',
            name='creation_date',
        ),
    ]
