# Generated by Django 4.2.11 on 2024-05-13 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BeyondComV2', '0002_remove_employe_departement_de_travail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventaire',
            name='sous_produit',
        ),
        migrations.AddField(
            model_name='employe',
            name='departement_de_travail',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='BeyondComV2.departement'),
        ),
        migrations.AlterField(
            model_name='produit',
            name='code_bar',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.DeleteModel(
            name='SousProduit',
        ),
    ]
