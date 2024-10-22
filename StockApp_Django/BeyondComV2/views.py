from django.shortcuts import render, get_object_or_404, redirect
from .models import Fournisseur, Employe, Produit, Inventaire, Departement, Event
from .forms import FournisseurForm, EmployeForm, ProduitForm, InventaireForm, DepartementForm, EventForm
from rest_framework import viewsets
from .serializers import FournisseurSerializer, EmployeSerializer, DepartementSerializer, ProduitSerializer, InventaireSerializer, EventSerializer
from django.db.models import Sum, F, Count
from django.http import HttpResponse
import csv

def home(request):
    # Calculate total number of products considering only IN products
    total_number_of_products = Inventaire.objects.filter(
        etat_InOut='IN'
    ).aggregate(total=Sum('quantite_produit'))['total'] or 0

    # Calculate total price of products considering only IN products
    total_price_of_products = Inventaire.objects.filter(
        etat_InOut='IN'
    ).aggregate(
        total=Sum(F('quantite_produit') * F('produit__prix'))
    )['total'] or 0

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



def fournisseur_list(request):
    fournisseurs = Fournisseur.objects.all()
    nom_query = request.GET.get('nom')
    tel_query = request.GET.get('tel')
    if nom_query:
        fournisseurs = fournisseurs.filter(fournisseur_name__icontains=nom_query)
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

def employe_list(request):
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    employes = Employe.objects.all()
    if search_query:
        employes = employes.filter(nom__icontains=search_query)
    if department_filter:
        employes = employes.filter(departement_de_travail__department_name=department_filter)
    departments = Departement.objects.all()
    return render(request, 'BeyondComV2/employe_list.html', {'employes': employes, 'departments': departments})

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

def produit_list(request):
    produits = Produit.objects.all()
    departments = Produit.objects.values_list('departement__department_name', flat=True).distinct()
    selected_department = request.GET.get('department')
    search_query = request.GET.get('search')
    code_bar_search_query = request.GET.get('code_bar_search')
    if selected_department:
        produits = produits.filter(departement__department_name=selected_department)
    if search_query:
        produits = produits.filter(produit_name__icontains=search_query)
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

# views.py - modify the inventaire_list view
from django.shortcuts import render
from django.db import models
from .models import Inventaire, Departement

def inventaire_list(request):
    inventaires = Inventaire.objects.select_related('produit', 'produit__departement').all()
    
    # Get filter parameters
    selected_department = request.GET.get('department', 'all')
    selected_state = request.GET.get('state', 'all')
    selected_etat = request.GET.get('etat', 'all')
    search_query = request.GET.get('search', '')

    # Apply filters
    if selected_department and selected_department.lower() != 'all':
        inventaires = inventaires.filter(produit__departement__department_name=selected_department)
            
    if selected_state and selected_state.lower() != 'all':
        inventaires = inventaires.filter(state=selected_state)
            
    if selected_etat and selected_etat.lower() != 'all':
        inventaires = inventaires.filter(etat_InOut=selected_etat)
            
    if search_query:
        inventaires = inventaires.filter(
            models.Q(produit__produit_name__icontains=search_query) |
            models.Q(produit__code_bar__icontains=search_query)
        )

    # Get choices for dropdowns
    departments = list(Departement.objects.values_list('department_name', flat=True))
    state_choices = [choice[0] for choice in Inventaire.state_choices]
    etat_choices = ['IN', 'OUT']

    context = {
        'inventaires': inventaires,
        'departments': departments,
        'state_choices': state_choices,
        'etat_choices': etat_choices,
        'selected_department': selected_department,
        'selected_state': selected_state,
        'selected_etat': selected_etat,
        'search_query': search_query,
    }

    return render(request, 'BeyondComV2/inventaire_list.html', context)

def download_produit_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="produits.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nom du Produit', 'Catégorie', 'Code Barre', 'Prix', 'Description', 'Fournisseur', 'Département', 'Période de Garantie (Mois)', 'Date de Début de Garantie', 'Date de Fin de Garantie', 'Garantie Valide'])
    produits = Produit.objects.all()
    selected_department = request.GET.get('department')
    search_query = request.GET.get('search')
    if selected_department:
        produits = produits.filter(departement__department_name=selected_department)
    if search_query:
        produits = produits.filter(produit_name__icontains=search_query)
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
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventaires.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Produit', 'Etat In/Out', 'Date In', 'Quantite Produit', 'Last Updated', 'State'])
    inventaires = Inventaire.objects.all()
    selected_department = request.GET.get('department')
    selected_state = request.GET.get('state')
    selected_etat = request.GET.get('etat')
    if selected_department:
        inventaires = inventaires.filter(produit__departement__department_name=selected_department)
    if selected_state:
        inventaires = inventaires.filter(state=selected_state)
    if selected_etat:
        inventaires = inventaires.filter(etat_InOut=selected_etat)
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
    current_in_products = Inventaire.objects.filter(etat_InOut='IN')
    current_out_products = Inventaire.objects.filter(etat_InOut='OUT')
    all_out_products = Inventaire.objects.filter(etat_InOut='OUT')
    
    return render(request, 'BeyondComV2/plus_de_details.html', {
        'current_in_products': current_in_products,
        'current_out_products': current_out_products,
        'all_out_products': all_out_products,
    })

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

def event_list(request):
    events = Event.objects.all().prefetch_related('list_of_products__produit')
    event_details = [{'event': event, 'products': event.list_of_products.all()} for event in events]
    return render(request, 'BeyondComV2/event_list.html', {'event_details': event_details})

# def event_create(request):
#     if request.method == 'POST':
#         form = EventForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('event_list')
#     else:
#         form = EventForm()
#     products = Inventaire.objects.filter(etat_InOut='IN', state='On').select_related('produit')
#     inventaires_with_details = [{
#         'inventaire_id': inv.inventaire_id,
#         'produit_name': inv.produit.produit_name,
#         'quantity': inv.quantite_produit
#     } for inv in products]
#     return render(request, 'BeyondComV2/event_form.html', {'form': form, 'inventaires_with_details': inventaires_with_details})

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Event, Inventaire
from .forms import EventProductForm

def event_create(request):
    if request.method == 'POST':
        form = EventProductForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Validate date sequence
                    event_data = form.cleaned_data
                    if not (event_data['event_pre_date'] <= event_data['event_start'] <= 
                           event_data['event_end'] <= event_data['event_post_date']):
                        raise ValidationError("Dates must be in sequence: pre_date ≤ start ≤ end ≤ post_date")

                    event = form.save(commit=False)
                    event.save()
                    
                    produits = form.cleaned_data['produits']
                    quantites = [int(q.strip()) for q in form.cleaned_data['quantites'].split(',')]
                    
                    if len(produits) != len(quantites):
                        raise ValidationError("Number of products and quantities must match")
                    
                    for produit, requested_quantity in zip(produits, quantites):
                        if requested_quantity <= 0:
                            raise ValidationError(f"Invalid quantity for {produit.produit.produit_name}")
                            
                        if requested_quantity > produit.quantite_produit:
                            raise ValidationError(
                                f"Requested quantity ({requested_quantity}) exceeds available quantity "
                                f"({produit.quantite_produit}) for {produit.produit.produit_name}"
                            )
                        
                        # Store old quantity and update inventory
                        old_quantity = produit.quantite_produit
                        remaining_quantity = old_quantity - requested_quantity
                        
                        # Update existing entry
                        produit.old_quantity = old_quantity
                        produit.quantite_produit = requested_quantity
                        produit.etat_InOut = 'OUT'
                        produit.save()
                        
                        # Create new entry for remaining quantity if any
                        if remaining_quantity > 0:
                            Inventaire.objects.create(
                                produit=produit.produit,
                                etat_InOut='IN',
                                date_in=produit.date_in,
                                quantite_produit=remaining_quantity,
                                state=produit.state
                            )
                        
                        event.list_of_products.add(produit)
                    
                    messages.success(request, 'Event created successfully.')
                    return redirect('event_list')
                    
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                
    else:
        form = EventProductForm()
    
    context = {
        'form': form,
        'available_inventory': Inventaire.objects.filter(
            etat_InOut='IN', 
            state='On'
        ).select_related('produit')
    }
    return render(request, 'BeyondComV2/event_form.html', context)


from django.db.models import F
from django.utils import timezone

def check_events(request):
    """
    Optional view to manually trigger event checking
    """
    current_time = timezone.now()
    
    # Find relevant events and trigger their signals
    events_to_check = Event.objects.filter(
        event_pre_date__lte=current_time,
        list_of_products__etat_InOut='IN'
    ).distinct()
    
    for event in events_to_check:
        event.save()
        
    events_to_return = Event.objects.filter(
        event_post_date__lte=current_time,
        list_of_products__etat_InOut='OUT'
    ).distinct()
    
    for event in events_to_return:
        event.save()
        
    messages.success(request, "Event status check completed")
    return redirect('event_list')  # or wherever you want to redirect

def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventProductForm(request.POST, instance=event)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Validate date sequence
                    event_data = form.cleaned_data
                    if not (event_data['event_pre_date'] <= event_data['event_start'] <= 
                           event_data['event_end'] <= event_data['event_post_date']):
                        raise ValidationError("Dates must be in sequence: pre_date ≤ start ≤ end ≤ post_date")

                    # Restore original quantities for current products
                    for product in event.list_of_products.all():
                        if product.old_quantity:
                            product.quantite_produit = product.old_quantity
                            product.old_quantity = None
                            product.etat_InOut = 'IN'
                            product.save()

                    event = form.save(commit=False)
                    event.save()
                    
                    # Clear existing products
                    event.list_of_products.clear()
                    
                    # Process new products and quantities
                    produits = form.cleaned_data['produits']
                    quantites = [int(q.strip()) for q in form.cleaned_data['quantites'].split(',')]
                    
                    if len(produits) != len(quantites):
                        raise ValidationError("Number of products and quantities must match")
                    
                    for produit, requested_quantity in zip(produits, quantites):
                        if requested_quantity <= 0:
                            raise ValidationError(f"Invalid quantity for {produit.produit.produit_name}")
                            
                        if requested_quantity > produit.quantite_produit:
                            raise ValidationError(
                                f"Requested quantity ({requested_quantity}) exceeds available quantity "
                                f"({produit.quantite_produit}) for {produit.produit.produit_name}"
                            )
                        
                        # Update inventory same as in create
                        old_quantity = produit.quantite_produit
                        remaining_quantity = old_quantity - requested_quantity
                        
                        produit.old_quantity = old_quantity
                        produit.quantite_produit = requested_quantity
                        produit.etat_InOut = 'OUT'
                        produit.save()
                        
                        if remaining_quantity > 0:
                            Inventaire.objects.create(
                                produit=produit.produit,
                                etat_InOut='IN',
                                date_in=produit.date_in,
                                quantite_produit=remaining_quantity,
                                state=produit.state
                            )
                        
                        event.list_of_products.add(produit)
                    
                    messages.success(request, 'Event updated successfully.')
                    return redirect('event_list')
                    
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = EventProductForm(instance=event)
        
    context = {
        'form': form,
        'event': event,
        'available_inventory': Inventaire.objects.filter(
            etat_InOut='IN', 
            state='On'
        ).select_related('produit')
    }
    return render(request, 'BeyondComV2/event_form.html', context)

def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Restore original quantities for all products
                for product in event.list_of_products.all():
                    if product.old_quantity:
                        product.quantite_produit = product.old_quantity
                        product.old_quantity = None
                        product.etat_InOut = 'IN'
                        product.save()
                
                event.delete()
                messages.success(request, 'Event deleted successfully.')
                return redirect('event_list')
        except Exception as e:
            messages.error(request, f"An error occurred while deleting the event: {str(e)}")
    return render(request, 'BeyondComV2/event_confirm_delete.html', {'event': event})

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer