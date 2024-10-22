# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from .models import Event, Inventaire

@receiver(post_save, sender=Event)
def check_event_status(sender, instance, created, **kwargs):
    """
    Signal handler to check and update inventory status whenever an event is accessed
    """
    try:
        current_time = timezone.now()
        
        with transaction.atomic():
            # Check if we need to process pre-date changes
            if current_time >= instance.event_pre_date:
                products_to_update = instance.list_of_products.filter(etat_InOut='IN')
                if products_to_update.exists():
                    success = instance.handle_event_pre_date()
                    if success:
                        print(f"Pre-date processing completed for event: {instance.event_name}")
                    else:
                        print(f"Pre-date processing failed for event: {instance.event_name}")

            # Check if we need to process post-date changes
            if current_time >= instance.event_post_date:
                products_to_update = instance.list_of_products.filter(etat_InOut='OUT')
                if products_to_update.exists():
                    success = instance.handle_event_post_date()
                    if success:
                        print(f"Post-date processing completed for event: {instance.event_name}")
                    else:
                        print(f"Post-date processing failed for event: {instance.event_name}")
    except Exception as e:
        print(f"Error in check_event_status signal: {str(e)}")