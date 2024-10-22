from django import forms
from django_select2.forms import Select2Widget
from .models import Fournisseur, Employe, Produit, Inventaire, Departement

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['fournisseur_name', 'tel']

class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['nom', 'poste', 'departement_de_travail', 'est_admin']

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['produit_name', 'category', 'prix', 'description', 'departement', 'fournisseur', 'warranty_period', 'warranty_start_date']
        widgets = {
            'fournisseur': Select2Widget,  # Apply Select2 to the fournisseur field
            'warranty_start_date': forms.DateInput(attrs={'type': 'date'})  # Change the widget for warranty_start_date to a date input
        }



class InventaireForm(forms.ModelForm):
    class Meta:
        model = Inventaire
        fields = ['produit', 'etat_InOut', 'date_in', 'quantite_produit', 'state']

class DepartementForm(forms.ModelForm):
    class Meta:
        model = Departement
        fields = ['department_name']

from django import forms
from .models import Event, Inventaire
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.widgets import DateInput
from django import forms
from .models import Event, Inventaire
from django.forms.widgets import DateTimeInput

from django import forms
from .models import Event, Inventaire
from django.forms.widgets import DateInput

class EventForm(forms.ModelForm):
    list_of_products = forms.ModelMultipleChoiceField(
        queryset=Inventaire.objects.filter(etat_InOut='IN', state='On').select_related('produit'),
        widget=forms.CheckboxSelectMultiple,
        label='Select Products'
    )

    class Meta:
        model = Event
        fields = ['event_name', 'event_pre_date', 'event_start', 'event_end', 'event_post_date', 'list_of_products']
        widgets = {
            'event_pre_date': forms.DateInput(attrs={'type': 'date'}),
            'event_start': forms.DateInput(attrs={'type': 'date'}),
            'event_end': forms.DateInput(attrs={'type': 'date'}),
            'event_post_date': forms.DateInput(attrs={'type': 'date'}),
        }


from django import forms
from .models import Event, Inventaire

# forms.py - modify the EventProductForm
class EventProductForm(forms.ModelForm):
    produits = forms.ModelMultipleChoiceField(
        queryset=Inventaire.objects.filter(etat_InOut='IN', state='On'),  # Modified filter
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Products"
    )
    quantites = forms.CharField(
        widget=forms.TextInput(),
        required=True,
        help_text="Enter quantities for selected products, separated by commas"
    )

    class Meta:
        model = Event
        fields = ['event_name', 'event_pre_date', 'event_start', 'event_end', 'event_post_date', 'produits', 'quantites']
