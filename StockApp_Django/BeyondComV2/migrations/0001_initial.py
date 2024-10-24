# Generated by Django 4.2.11 on 2024-05-03 15:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Departement',
            fields=[
                ('departement_id', models.AutoField(primary_key=True, serialize=False)),
                ('department_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Fournisseur',
            fields=[
                ('fournisseur_id', models.AutoField(primary_key=True, serialize=False)),
                ('fournisseur_name', models.CharField(max_length=100)),
                ('tel', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Produit',
            fields=[
                ('produit_id', models.AutoField(primary_key=True, serialize=False)),
                ('produit_name', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('code_bar', models.CharField(max_length=100)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=12)),
                ('description', models.TextField()),
                ('departement', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='BeyondComV2.departement')),
                ('fournisseur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BeyondComV2.fournisseur')),
            ],
        ),
        migrations.CreateModel(
            name='SousProduit',
            fields=[
                ('sous_produit_id', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=100)),
                ('etat', models.CharField(max_length=100)),
                ('produits', models.ManyToManyField(to='BeyondComV2.produit')),
            ],
        ),
        migrations.CreateModel(
            name='Inventaire',
            fields=[
                ('inventaire_id', models.AutoField(primary_key=True, serialize=False)),
                ('etat_InOut', models.CharField(choices=[('IN', 'IN'), ('OUT', 'OUT')], default='IN', max_length=20)),
                ('date_in', models.DateField()),
                ('quantite_produit', models.IntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(choices=[('On', 'On'), ('Off', 'Off'), ('Maintenance', 'Maintenance')], default='On', max_length=20)),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BeyondComV2.produit')),
                ('sous_produit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='BeyondComV2.sousproduit')),
            ],
        ),
        migrations.CreateModel(
            name='Employe',
            fields=[
                ('employe_id', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=100)),
                ('poste', models.CharField(max_length=100)),
                ('est_admin', models.BooleanField(default=False)),
                ('departement_de_travail', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='BeyondComV2.departement')),
            ],
        ),
        migrations.AddField(
            model_name='departement',
            name='chef_de_departement',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='BeyondComV2.employe'),
        ),
    ]
