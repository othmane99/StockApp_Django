from django.utils import timezone
from .models import Event

class EventCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check events before processing the request
        current_time = timezone.now()
        
        # Get events that need processing
        events_to_check = Event.objects.filter(
            event_pre_date__lte=current_time,
            list_of_products__etat_InOut='IN'
        ).distinct()
        
        for event in events_to_check:
            event.save()  # This will trigger the signal
            
        events_to_return = Event.objects.filter(
            event_post_date__lte=current_time,
            list_of_products__etat_InOut='OUT'
        ).distinct()
        
        for event in events_to_return:
            event.save()  # This will trigger the signal

        response = self.get_response(request)
        return response