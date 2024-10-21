import uuid
from django.contrib import admin
from .models import Fournisseur, Departement, Employe, Produit, Inventaire, Event, Bucket

# Register your models here.

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ['fournisseur_id', 'fournisseur_name', 'tel']

@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ['departement_id', 'department_name']

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ['employe_id', 'nom', 'poste', 'departement_de_travail', 'est_admin']


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['produit_id', 'produit_name', 'category', 'code_bar', 'prix', 'description', 'fournisseur', 'departement', 'warranty_period', 'warranty_start_date', 'warranty_end_date', 'warranty_isValid']
    readonly_fields = ('code_bar',)

    def save_model(self, request, obj, form, change):
        if not obj.code_bar:
            department_id_str = str(obj.departement.departement_id).zfill(2)
            obj.code_bar = department_id_str + uuid.uuid4().hex[:10]
        obj.save()


@admin.register(Inventaire)
class InventaireAdmin(admin.ModelAdmin):
    list_display = ['inventaire_id', 'produit', 'etat_InOut', 'date_in', 'quantite_produit', 'last_updated', 'state']


######################################################################################################3

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'event_name', 'event_pre_date', 'event_start', 'event_end', 'event_post_date']
    list_filter = ['event_start', 'event_end']
    search_fields = ['event_name']
    filter_horizontal = ['list_of_products']

@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ['bucket_id', 'barcode']
    search_fields = ['barcode']
    filter_horizontal = ['products']