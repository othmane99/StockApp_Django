from django.shortcuts import render, get_object_or_404, redirect
from .models import Fournisseur, Employe, Produit, Inventaire, Departement, Event
from .forms import FournisseurForm, EmployeForm, ProduitForm, InventaireForm, DepartementForm, EventForm
from rest_framework import viewsets
from .serializers import FournisseurSerializer, EmployeSerializer, DepartementSerializer, ProduitSerializer, InventaireSerializer, EventSerializer
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import csv
from django.db.models import Sum, F
from django.template.loader import render_to_string
from django.db.models import Count, Case, When, Value, IntegerField



def home(request):
    # Calculate total number of products considering the quantity in the inventory
    total_number_of_products = Inventaire.objects.aggregate(total=Sum('quantite_produit'))['total'] or 0

    # Calculate total price of products considering the quantity in the inventory
    total_price_of_products = Inventaire.objects.aggregate(total=Sum(F('quantite_produit') * F('produit__prix')))['total'] or 0

    # Calculate the number of valid and expired warranties
    valid_warranties = Produit.objects.filter(warranty_isValid=True).count()
    expired_warranties = Produit.objects.filter(warranty_isValid=False).count()

    # Prepare data for product statistics chart
    product_statistics = Inventaire.objects.values('produit__category').annotate(total=Sum('quantite_produit'))
    product_statistics_data = {
        'labels': [entry['produit__category'] for entry in product_statistics],
        'datasets': [{
            'label': 'Product Count',
            'data': [entry['total'] for entry in product_statistics],
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1
        }]
    }

    # Prepare data for department-wise product count chart
    department_product_count = Departement.objects.annotate(total_products=Sum('produit__inventaire__quantite_produit'))
    department_product_count_data = {
        'labels': [entry.department_name for entry in department_product_count],
        'datasets': [{
            'label': 'Product Count',
            'data': [entry.total_products or 0 for entry in department_product_count],
            'backgroundColor': 'rgba(153, 102, 255, 0.2)',
            'borderColor': 'rgba(153, 102, 255, 1)',
            'borderWidth': 1
        }]
    }

    # Calculate inventory state distribution
    inventory_state_distribution = Inventaire.objects.values('state').annotate(total=Sum('quantite_produit'))
    inventory_state_distribution_data = {
        'labels': [entry['state'] for entry in inventory_state_distribution],
        'datasets': [{
            'label': 'Inventory State Distribution',
            'data': [entry['total'] for entry in inventory_state_distribution],
            'backgroundColor': [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            'borderColor': [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            'borderWidth': 1
        }]
    }

    # Prepare data for warranty status distribution chart
    warranty_status_distribution_data = {
        'labels': ['Valid Warranties', 'Expired Warranties'],
        'datasets': [{
            'label': 'Warranty Status Distribution',
            'data': [valid_warranties, expired_warranties],
            'backgroundColor': [
                'rgba(75, 192, 192, 0.2)',
                'rgba(255, 99, 132, 0.2)'
            ],
            'borderColor': [
                'rgba(75, 192, 192, 1)',
                'rgba(255, 99, 132, 1)'
            ],
            'borderWidth': 1
        }]
    }

    context = {
        'inventory_state_distribution_data': inventory_state_distribution_data,
        'total_number_of_products': total_number_of_products,
        'total_price_of_products': total_price_of_products,
        'product_statistics_data': product_statistics_data,
        'department_product_count_data': department_product_count_data,
        'valid_warranties': valid_warranties,
        'expired_warranties': expired_warranties,
        'warranty_status_distribution_data': warranty_status_distribution_data
    }

    return render(request, 'home.html', context)








# Votre vue pour la liste des fournisseurs
def fournisseur_list(request):
    fournisseurs = Fournisseur.objects.all()

    # Filtrage par nom
    nom_query = request.GET.get('nom')
    if nom_query:
        fournisseurs = fournisseurs.filter(fournisseur_name__icontains=nom_query)

    # Filtrage par numéro de téléphone
    tel_query = request.GET.get('tel')
    if tel_query:
        fournisseurs = fournisseurs.filter(tel__icontains=tel_query)

    return render(request, 'BeyondComV2/fournisseur_list.html', {'fournisseurs': fournisseurs})


def fournisseur_create(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm()
    return render(request, 'BeyondComV2/fournisseur_form.html', {'form': form})


def fournisseur_update(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'BeyondComV2/fournisseur_form.html', {'form': form})

def fournisseur_delete(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        return redirect('fournisseur_list')
    return render(request, 'BeyondComV2/fournisseur_confirm_delete.html', {'fournisseur': fournisseur})

# Employe views
def employe_list(request):
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')

    employes = Employe.objects.all()

    if search_query:
        employes = employes.filter(nom__icontains=search_query)
    
    if department_filter:
        employes = employes.filter(departement_de_travail__department_name=department_filter)

    departments = Departement.objects.all()
    
    context = {
        'employes': employes,
        'departments': departments
    }
    
    return render(request, 'BeyondComV2/employe_list.html', context)

def employe_create(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employe_list')
    else:
        form = EmployeForm()
    return render(request, 'BeyondComV2/employe_form.html', {'form': form})

def employe_update(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    if request.method == 'POST':
        form = EmployeForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            return redirect('employe_list')
    else:
        form = EmployeForm(instance=employe)
    return render(request, 'BeyondComV2/employe_form.html', {'form': form})

def employe_delete(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    if request.method == 'POST':
        employe.delete()
        return redirect('employe_list')
    return render(request, 'BeyondComV2/employe_confirm_delete.html', {'employe': employe})



from django.shortcuts import render, get_object_or_404, redirect
from .models import Produit
from .forms import ProduitForm

def produit_list(request):
    produits = Produit.objects.all()

    # Liste des départements
    departments = Produit.objects.values_list('departement__department_name', flat=True).distinct()

    # Filtrer par département
    selected_department = request.GET.get('department')
    if selected_department:
        produits = produits.filter(departement__department_name=selected_department)

    # Fonctionnalité de recherche
    search_query = request.GET.get('search')
    if search_query:
        produits = produits.filter(produit_name__icontains=search_query)

    # Recherche par code barre
    code_bar_search_query = request.GET.get('code_bar_search')
    if code_bar_search_query:
        produits = produits.filter(code_bar__icontains=code_bar_search_query)

    return render(request, 'BeyondComV2/produit_list.html', {'produits': produits, 'departments': departments})


def produit_create(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('produit_list')
    else:
        form = ProduitForm()
    return render(request, 'BeyondComV2/produit_form.html', {'form': form})


def produit_update(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('produit_list')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'BeyondComV2/produit_form.html', {'form': form, 'produit': produit})


def produit_delete(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        return redirect('produit_list')
    return render(request, 'BeyondComV2/produit_confirm_delete.html', {'produit': produit})



from django.db.models import Count, Q
from django.shortcuts import render
from .models import Inventaire, Produit

def inventaire_list(request):
    inventaires = Inventaire.objects.all()

    # Liste des états
    state_choices = Inventaire.state_choices

    # Fetch unique department names from related Produit model
    departments = Produit.objects.values_list('departement__department_name', flat=True).distinct()

    # Filter by department
    selected_department = request.GET.get('department')
    if selected_department:
        inventaires = inventaires.filter(produit__departement__department_name=selected_department)

    # Filter by state
    selected_state = request.GET.get('state')
    if selected_state:
        inventaires = inventaires.filter(state=selected_state)

    # Filter by etat
    selected_etat = request.GET.get('etat')
    if selected_etat:
        inventaires = inventaires.filter(etat_InOut=selected_etat)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        inventaires = inventaires.filter(produit__produit_name__icontains=search_query)

    # Check warranty for each product
    for inventaire in inventaires:
        inventaire.produit.warranty_isValid = inventaire.produit.warranty_isValid

    return render(request, 'BeyondComV2/inventaire_list.html', {
        'inventaires': inventaires,
        'departments': departments,
        'state_choices': state_choices,
        'selected_department': selected_department,
        'selected_state': selected_state,
        'selected_etat': selected_etat,
        'search_query': search_query,
    })

import csv
from django.http import HttpResponse
from .models import Produit

def download_produit_csv(request):
    # Initialisation de la réponse HTTP avec le type MIME pour un fichier CSV
    response = HttpResponse(content_type='text/csv')
    # Définition du nom du fichier de téléchargement
    response['Content-Disposition'] = 'attachment; filename="produits.csv"'

    # Écriture du contenu CSV
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nom du Produit', 'Catégorie', 'Code Barre', 'Prix', 'Description', 'Fournisseur', 'Département', 'Période de Garantie (Mois)', 'Date de Début de Garantie', 'Date de Fin de Garantie', 'Garantie Valide'])  # En-tête

    # Récupération des données filtrées en fonction des paramètres de requête
    produits = Produit.objects.all()

    # Filtrer par département si présent dans la requête
    selected_department = request.GET.get('department')
    if selected_department:
        produits = produits.filter(departement__department_name=selected_department)

    # Fonctionnalité de recherche
    search_query = request.GET.get('search')
    if search_query:
        produits = produits.filter(produit_name__icontains=search_query)

    # Écriture des lignes de données
    for produit in produits:
        writer.writerow([
            produit.produit_id,
            produit.produit_name,
            produit.category,
            produit.code_bar,
            produit.prix,
            produit.description,
            produit.fournisseur.fournisseur_name if produit.fournisseur else '',
            produit.departement.department_name if produit.departement else '',
            produit.warranty_period,
            produit.warranty_start_date,
            produit.warranty_end_date,
            'Oui' if produit.warranty_isValid else 'Non'
        ])

    return response



def download_inventaire_csv(request):
    # Initialisation de la réponse HTTP avec le type MIME pour un fichier CSV
    response = HttpResponse(content_type='text/csv')
    # Définition du nom du fichier de téléchargement
    response['Content-Disposition'] = 'attachment; filename="inventaires.csv"'

    # Écriture du contenu CSV
    writer = csv.writer(response)
    writer.writerow(['ID', 'Produit', 'Etat In/Out', 'Date In', 'Quantite Produit', 'Last Updated', 'State'])  # En-tête

    # Récupération des données filtrées en fonction des paramètres de requête
    inventaires = Inventaire.objects.all()

    # Filtrer par département si présent dans la requête
    selected_department = request.GET.get('department')
    if selected_department:
        inventaires = inventaires.filter(produit__departement__department_name=selected_department)

    # Filtrer par état si présent dans la requête
    selected_state = request.GET.get('state')
    if selected_state:
        inventaires = inventaires.filter(state=selected_state)

    # Filtrer par état In/Out si présent dans la requête
    selected_etat = request.GET.get('etat')
    if selected_etat:
        inventaires = inventaires.filter(etat_InOut=selected_etat)

    # Écriture des lignes de données
    for inventaire in inventaires:
        writer.writerow([
            inventaire.inventaire_id,
            inventaire.produit.produit_name,
            inventaire.etat_InOut,
            inventaire.date_in,
            inventaire.quantite_produit,
            inventaire.last_updated,
            inventaire.state
        ])

    return response


def inventaire_create(request):
    if request.method == 'POST':
        form = InventaireForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventaire_list')
    else:
        form = InventaireForm()
    return render(request, 'BeyondComV2/inventaire_form.html', {'form': form})

def inventaire_update(request, pk):
    inventaire = get_object_or_404(Inventaire, pk=pk)
    if request.method == 'POST':
        form = InventaireForm(request.POST, instance=inventaire)
        if form.is_valid():
            form.save()
            return redirect('inventaire_list')
    else:
        form = InventaireForm(instance=inventaire)
    return render(request, 'BeyondComV2/inventaire_form.html', {'form': form})

def inventaire_delete(request, pk):
    inventaire = get_object_or_404(Inventaire, pk=pk)
    if request.method == 'POST':
        inventaire.delete()
        return redirect('inventaire_list')
    return render(request, 'BeyondComV2/inventaire_confirm_delete.html', {'inventaire': inventaire})

# Departement views
def departement_list(request):
    departements = Departement.objects.all()
    return render(request, 'BeyondComV2/departement_list.html', {'departements': departements})

def departement_create(request):
    if request.method == 'POST':
        form = DepartementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('departement_list')
    else:
        form = DepartementForm()
    return render(request, 'BeyondComV2/departement_form.html', {'form': form})

def departement_update(request, pk):
    departement = get_object_or_404(Departement, pk=pk)
    if request.method == 'POST':
        form = DepartementForm(request.POST, instance=departement)
        if form.is_valid():
            form.save()
            return redirect('departement_list')
    else:
        form = DepartementForm(instance=departement)
    return render(request, 'BeyondComV2/departement_form.html', {'form': form})

def departement_delete(request, pk):
    departement = get_object_or_404(Departement, pk=pk)
    if request.method == 'POST':
        departement.delete()
        return redirect('departement_list')
    return render(request, 'BeyondComV2/departement_confirm_delete.html', {'departement': departement})


def plus_de_details(request):
    # Retrieve current IN products (etat_InOut = 'IN')
    current_in_products = Inventaire.objects.filter(etat_InOut='IN')

    # Retrieve current OUT products (etat_InOut = 'OUT')
    current_out_products = Inventaire.objects.filter(etat_InOut='OUT')

    # Retrieve all OUT products
    all_out_products = Inventaire.objects.filter(etat_InOut='OUT')

    # Render the template with the provided context
    return render(request, 'BeyondComV2/plus_de_details.html', {
        'current_in_products': current_in_products,
        'current_out_products': current_out_products,
        'all_out_products': all_out_products,
    })


# ViewSets for the REST API
class FournisseurViewSet(viewsets.ModelViewSet):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer

class EmployeViewSet(viewsets.ModelViewSet):
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

class DepartementViewSet(viewsets.ModelViewSet):
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

class InventaireViewSet(viewsets.ModelViewSet):
    queryset = Inventaire.objects.all()
    serializer_class = InventaireSerializer

############################################################################################################


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Event, Inventaire
from .forms import EventForm
import uuid

def event_list(request):
    events = Event.objects.all().prefetch_related('list_of_products__produit')
    event_details = []
    for event in events:
        event_detail = {
            'event': event,
            'products': event.list_of_products.all()
        }
        event_details.append(event_detail)
    return render(request, 'BeyondComV2/event_list.html', {'event_details': event_details})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Inventaire
from django.contrib import messages
from .forms import EventForm

def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_list')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = EventForm()

    products = Inventaire.objects.filter(etat_InOut='IN', state='On').select_related('produit')
    inventaires_with_details = [{
        'inventaire_id': inv.inventaire_id,
        'produit_name': inv.produit.produit_name,
        'quantity': inv.quantite_produit
    } for inv in products]

    return render(request, 'BeyondComV2/event_form.html', {'form': form, 'inventaires_with_details': inventaires_with_details})


def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)

    products = Inventaire.objects.filter(etat_InOut='IN', state='On').select_related('produit')
    inventaires_with_details = [{
        'inventaire_id': inv.inventaire_id,
        'produit_name': inv.produit.produit_name,
        'quantity': inv.quantite_produit
    } for inv in products]

    return render(request, 'BeyondComV2/event_form.html', {'form': form, 'inventaires_with_details': inventaires_with_details})


def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'BeyondComV2/event_confirm_delete.html', {'event': event})
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer