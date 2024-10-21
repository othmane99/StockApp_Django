from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Event, Inventaire

@receiver(post_save, sender=Event)
def update_inventory_status(sender, instance, created, **kwargs):
    if created:  # Vérifie si l'événement est nouvellement créé
        # Gérer l'état des produits dans l'inventaire
        print("event created")
        instance.handle_event_pre_date()
        instance.handle_event_post_date()