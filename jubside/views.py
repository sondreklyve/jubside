from django.views.generic import ListView
from events.models import Event

# Create your views here.

class FrontPageView(ListView):
    template_name = 'jubside_frontpage.html'

    model = Event

    queryset = Event.objects.order_by('event_start')

    def get_context_data(self, **kwargs):
        context = super(FrontPageView, self).get_context_data(**kwargs)
        return context
