import re
from uuid import UUID
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.template import loader
from django.views.generic import TemplateView, DetailView
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied

import datetime
from itertools import chain
from braces.views import (PermissionRequiredMixin,
                          LoginRequiredMixin,
                          StaticContextMixin,
                          MessageMixin)

from .event_overrides import get_eventgetter

from .models import Event, EventRegistration
from .exceptions import *
from .event_calendar import EventCalendar


class AdminLinksMixin(object):
    """
    Adds links to the admin page for an object to the context.

    Meant to be used together with DetailView.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        view_name = "admin:{app_label}_{model_name}_{action}"
        context["change_url"] = reverse(view_name.format(action="change", **locals()), args=[self.object.id])
        context["delete_url"] = reverse(view_name.format(action="delete", **locals()), args=[self.object.id])
        return context


User = get_user_model()
EventGetter = get_eventgetter()

class TicketView(LoginRequiredMixin,
                DetailView):
    model = Event
    context_object_name = 'reg'
    template_name = "events/event_ticket.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        number = self.request.GET.get('number')
        if not number:
            number = 1
        try:
            user_number = str(EventRegistration.objects.get(event=event, user=self.request.user).number)
        except EventRegistration.DoesNotExist:
            user_number = 0
        reg = EventRegistration.objects.get(event=event, number=number)
        context.update({'user': self.request.user,
                        'permission': self.request.user.has_perm('events.administer'),
                        'first_name': reg.user.first_name,
                        'last_name': reg.user.last_name,
                        'email': reg.user.email,
                        'allergies': reg.user.allergies,
                        'starting_year': reg.user.starting_year,
                        'has_paid': reg.has_paid,
                        'ticket_id': reg.ticket_id,
                        'checked_in': reg.checked_in,
                        'check_in_time': reg.check_in_time,
                        'number': number,
                        'user_number': user_number})

        return context


class TicketCheckView(PermissionRequiredMixin,
                      DetailView):
    model = Event
    context_object_name = 'reg'
    template_name = "events/event_ticket_check.html"
    permission_required = 'events.administer'

    def post(self, request, pk):
        """Sjekker inn brukeren i POST['text'] hvis id-en tilhører en bruker som har betalt."""
        text = request.POST.get('text')
        try:
            ticket_id = UUID(text, version=4)
        except ValueError:
            return HttpResponseRedirect(reverse("check_in", kwargs={'pk': pk}))

        try:
            event = self.get_object()
            try:
                reg = EventRegistration.objects.get(event=event, ticket_id=ticket_id)
            except EventRegistration.DoesNotExist:
                return HttpResponseRedirect(reverse("check_in", kwargs={'pk': pk}))
            copy = False
            if not reg.checked_in:
                reg.checked_in = True
                reg.check_in_time = datetime.datetime.now()
                reg.save()
            else:
                copy = True
            return HttpResponseRedirect("%s%s%s" % (reverse("check_in", kwargs={'pk': pk}), "?num=" + str(reg.number), "&copy=" + str(copy)))

        except (Event.DoesNotExist, EventRegistration.DoesNotExist):
            pass


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        number = self.request.GET.get('num')
        copy = self.request.GET.get('copy')
        total_checked_in = EventRegistration.objects.filter(event=event, checked_in = True).count() ## Number of people currently checked in
        total_registrations = EventRegistration.objects.filter(event=event).count() ## Number of registrations for the event
        context.update({'total_checked_in': total_checked_in,
                        'total_registrations': total_registrations,
                        'event_name': event.headline})
        if not number:
            context.update({'is_ticket': False})
            
        else:
            reg = EventRegistration.objects.get(event=event, number=number)
            context.update({'first_name': reg.user.first_name,
                       'last_name': reg.user.last_name,
                       'email': reg.user.email,
                       'allergies': reg.user.allergies,
                       'starting_year': reg.user.starting_year,
                       'has_paid': reg.has_paid,
                       'checked_in': reg.checked_in,
                       'check_in_time': reg.check_in_time,
                       'number': number,
                       'copy': copy,
                       'is_ticket': True}

            )
        return context


class AdministerRegistrationsView(StaticContextMixin,
                                  PermissionRequiredMixin,
                                  DetailView):
    """Viser påmeldingslisten til et Event med mulighet for å melde folk på og av."""
    model = Event
    template_name = "events/event_administer.html"
    permission_required = 'events.administer'
    actions = {"pay_mail": ("Bekreft betaling og send billett", "pay_ticket"),
               "mail": ("Send billett via mail", "send_ticket"),
               "pay": ("Bekreft betaling", "set_paid_user"),
               "add": ("Legg til deltager", "register_user"),
               "del": ("Fjern deltager", "deregister_users")
               }
    static_context = {'actions': [(key, name) for key, (name, _) in actions.items()]}

    def post(self, request, pk):
        action_key = request.POST.get('action')
        name, method = self.actions[action_key]
        getattr(self, method)()
        return HttpResponseRedirect(reverse('event_admin', kwargs={'pk': pk}))

    def register_user(self):
        """Melder på brukeren nevnt i POST['text'] på arrangementet."""
        text = self.request.POST.get('text')
        m = re.findall('([^\s]+)', text, re.IGNORECASE)
        for username in m:
            try:
                user = User.objects.get(username=username)
                self.get_object().add_to_attending_or_waiting_list(user)
            except (User.DoesNotExist, UserRegistrationException):
                pass

    def deregister_users(self):
        """Melder av brukerne nevnt i POST['user']."""
        user_list = self.request.POST.getlist('user')
        for username in user_list:
            try:
                user = User.objects.get(username=username)
                self.get_object().force_deregister_user(user)
            except (User.DoesNotExist, UserRegistrationException):
                pass

    def set_paid_user(self):
        user_list = self.request.POST.getlist('user')
        for username in user_list:
            try:
                user = User.objects.get(username=username)
                self.get_object().set_paid_user(user)
            except (User.DoesNotExist, UserRegistrationException):
                pass

    def send_ticket(self):
        user_list = self.request.POST.getlist('user')
        for username in user_list:
            try:
                user = User.objects.get(username=username)
                self.get_object().send_ticket(user)
            except (User.DoesNotExist, UserRegistrationException):
                pass

    def pay_ticket(self):
        self.set_paid_user()
        self.send_ticket()


def calendar(request, year=None, month=None):
    """
    Renders a calendar with models from the chosen month
    """
    today = datetime.date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month
    try:
        first_of_month = datetime.date(year, month, 1)
    except ValueError:  # Not a valid year and month
        raise Http404

    events = EventGetter.get_current_events(year, month)
    cal = EventCalendar(chain(events)).formatmonth(year, month)

    user = request.user
    future_attending_events = EventGetter.attending_events(user, today)

    # Get some random dates in the current, next, and previous month.
    # These dates are used load the calendar for that month.
    # * prev is some day in the previous month
    # * this is some day in this month
    # * next is some day in the next month
    return render(request, 'events/event_list.html', {
        'calendar': mark_safe(cal),
        'prev': first_of_month - datetime.timedelta(27),
        'this': first_of_month,
        'next': first_of_month + datetime.timedelta(32),
        'future_attending_events': future_attending_events,
    })


class EventRegistrationsView(PermissionRequiredMixin, DetailView):
    """Viser en liste over alle brukere påmeldt til arrangementet."""
    model = Event
    context_object_name = "event"
    template_name = "events/event_registrations.html"
    permission_required = 'events.add_event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        context['eventregistrations'] = event.eventregistration_set.order_by('-attending', 'user__last_name')
        return context


class EventDetailView(AdminLinksMixin, MessageMixin, DetailView):
    """Viser arrangementet."""
    model = Event
    context_object_name = "event"
    template_name = 'events/event_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        user = self.request.user

        if user.is_authenticated():
            # Innlogget, så sjekk om de er påmeldt
            try:
                context['is_authenticated'] = True
                context['is_registered'] = event.is_registered(user)
                context['is_attending'] = event.is_attending(user)
                context['is_waiting'] = event.is_waiting(user)
                context['has_paid'] = event.has_paid(user)
                context['ticket_url_end'] = "?number=" + str(event.get_place(user))
                context['ended'] = event.has_finished()
            except EventException as e:
                self.messages.error(e)
        else:
            context['is_authenticated'] = False
        return context

class EventSummaryView(DetailView):
    model = Event
    context_object_name = "event"
    template_name = 'events/event_summary.html'

    def get_context_data(self, **kwargs):
        if not self.request.user.has_perm('events.administer'):
            raise PermissionDenied
        
        event = self.object
                
        if not event.has_finished():
            raise PermissionDenied("Summary kun tilgjengelig etter at arrangementet er avsluttet.")
        
        context = super().get_context_data(**kwargs)
        regs = event.attending_registrations

        too_late = regs.filter(checked_in = True, check_in_time__gte = self.object.event_start + datetime.timedelta(minutes = 10) )
        
        context['did_not_attend'] = regs.filter(checked_in = False)
        context['checked_in_late'] = too_late 
        return context


class UserEventView(LoginRequiredMixin, TemplateView):
    template_name = 'events/event_showuser.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        user = self.request.user
        context_data['user'] = user
        if user.is_authenticated():
            regs = user.eventregistration_set.all().order_by('event__event_start')
            context_data['eventregistration_list'] = regs
            context_data['is_on_a_waiting_list'] = regs.filter(attending=False).exists()
            context_data['is_attending_an_event'] = regs.filter(attending=True).exists()
        return context_data


class RegisterUserView(LoginRequiredMixin,
                       MessageMixin,
                       DetailView):
    """View for at en bruker skal kunne melde seg av og på."""

    model = Event
    template_name = 'events/event_detail.html'

    def post(self, *args, **kwargs):
        reg_type = self.request.POST['registration_type']
        user = self.request.user

        if reg_type == "registration":
            message = self.register_user(user)
        elif reg_type == "deregistration":
            message = self.deregister_user(user)
        else:
            message = "Her skjedde det noe galt."

        self.messages.info(message)
        return HttpResponseRedirect(self.get_object().get_absolute_url())

    def register_user(self, user):
        """Prøver å melde en bruker på arrangementet.

        Returnerer en melding som er ment for brukeren.
        """
        try:
            reg = self.get_object().register_user(user)
        except EventFullException:
            return "Arrangementet er fullt"
        except RegistrationNotAllowed:
            return 'Du har ikke lov til å melde deg på dette arrangementet.'
        except RegistrationNotOpen:
            return 'Påmeldingen er ikke åpen.'
        except RegistrationAlreadyExists:
            return "Du er allerede påmeldt."
        except RegistrationNotRequiredException:
            return "Arrangementet har ikke påmelding."
        return "Du er påmeldt" if reg.attending else "Du står nå på venteliste."

    def deregister_user(self, user):
        """Prøver å melde en bruker av arrangementet.

        Returnerer en melding som er ment for brukeren.
        """
        try:
            self.get_object().deregister_user(user)
        except DeregistrationClosed:
            return "Avmeldingsfristen er ute."
        else:
            return "Du er meldt av arrangementet."


def ical_event(request, event_id):
    """Returns a given event or bedpres as an iCal .ics file"""

    event = Event.objects.get(id=event_id)

    # Use the same template for both Event and BedPres.
    template = loader.get_template('events/event_icalendar.ics')
    context = {'event_list': (event,), }
    response = HttpResponse(template.render(context), content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename=Nabla_%s.ics' % event.slug
    return response
