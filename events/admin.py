from django.contrib import admin
from image_cropping import ImageCroppingMixin

from .forms import EventForm
from .models import Event, EventRegistration

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    readonly_fields=('ticket_id',)


class ChangedByMixin(object):
    def save_model(self, request, obj, form, change):
        obj.last_changed_by = request.user

        # Update created_by
        if getattr(obj, 'created_by', None) is None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Event)
class EventAdmin(ImageCroppingMixin, ChangedByMixin, admin.ModelAdmin):
    fields = ("publication_date",
              "published",
		      "hidden_to_guests",
              "event_picture",
              "event_cropping",
              "front_picture",
              "front_cropping",
              "headline",
              "slug",
              "short_name",
              "lead_paragraph",
              "body",
              "organizer",
              "location",
              "event_start",
              "event_end",
              "registration_required",
              "registration_deadline",
              "registration_start",
              "deregistration_deadline",
              "places",
              "has_queue",
              "open_for",
              "facebook_url",
              )
    form = EventForm
    list_display = ['__str__', 'registration_required']
    date_hierarchy = 'event_start'
    ordering = ['-event_start']
    search_fields = ['headline', 'body']
    list_filter = ['event_start', 'organizer', 'location']
    actions_on_top = True
