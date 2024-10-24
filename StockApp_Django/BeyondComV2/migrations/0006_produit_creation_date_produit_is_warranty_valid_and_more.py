# Generated by Django 4.2.11 on 2024-05-22 09:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BeyondComV2', '0005_alter_produit_code_bar'),
    ]

    operations = [
        migrations.AddField(
            model_name='produit',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='produit',
            name='is_warranty_valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='produit',
            name='warranty_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='produit',
            name='warranty_period',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
