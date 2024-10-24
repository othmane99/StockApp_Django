from django.urls import path
from . import views
from .views import (
    home,
    fournisseur_list, fournisseur_create, fournisseur_update, fournisseur_delete,
    employe_list, employe_create, employe_update, employe_delete,
    produit_list, produit_create, produit_update, produit_delete,
    inventaire_list, inventaire_create, inventaire_update, inventaire_delete,
    departement_list, departement_create, departement_update, departement_delete, 
    download_produit_csv, download_inventaire_csv, plus_de_details, 
    event_list, event_create, event_update, event_delete
)

urlpatterns = [
    path('', home, name='home'),
    path('plus-de-details/', plus_de_details, name='plus_de_details'),
    path('fournisseurs/', fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/create/', fournisseur_create, name='fournisseur_create'),
    path('fournisseurs/<int:pk>/edit/', fournisseur_update, name='fournisseur_update'),
    path('fournisseurs/<int:pk>/delete/', fournisseur_delete, name='fournisseur_delete'),

    path('employes/', employe_list, name='employe_list'),
    path('employes/create/', employe_create, name='employe_create'),
    path('employes/<int:pk>/edit/', employe_update, name='employe_update'),
    path('employes/<int:pk>/delete/', employe_delete, name='employe_delete'),

    path('produits/', produit_list, name='produit_list'),
    path('download_produit_csv/', download_produit_csv, name='download_produit_csv'),
    path('produits/create/', produit_create, name='produit_create'),
    path('produits/<int:pk>/edit/', produit_update, name='produit_update'),
    path('produits/<int:pk>/delete/', produit_delete, name='produit_delete'),

    path('inventaires/', inventaire_list, name='inventaire_list'),
    path('download_inventaire_csv/', download_inventaire_csv, name='download_inventaire_csv'),
    path('inventaires/create/', inventaire_create, name='inventaire_create'),
    path('inventaires/<int:pk>/edit/', inventaire_update, name='inventaire_update'),
    path('inventaires/<int:pk>/delete/', inventaire_delete, name='inventaire_delete'),

    path('departements/', departement_list, name='departement_list'),
    path('departements/create/', departement_create, name='departement_create'),
    path('departements/<int:pk>/edit/', departement_update, name='departement_update'),
    path('departements/<int:pk>/delete/', departement_delete, name='departement_delete'),

    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/update/<int:pk>/', views.event_update, name='event_update'),
    path('events/delete/<int:pk>/', views.event_delete, name='event_delete'),

]
