import logging
from django.urls import reverse

from django.contrib.sites.models import Site
from image_cropping.fields import ImageRatioField
from ..exceptions import RegistrationAlreadyExists, EventFullException, DeregistrationClosed
from .abstract_event import AbstractEvent
from .eventregistration import EventRegistration
from django.db import models
from django.conf import settings

class WithEventPicture(models.Model):
    event_picture = models.ImageField(
        upload_to="uploads/event_pictures",
        null=True,
        blank=True,
        verbose_name="Arrangementbilde",
        help_text="Bilder som er større enn 1000x400 px ser best ut. Du kan beskjære bildet etter opplasting."
    )

    event_cropping = ImageRatioField(
        'event_picture',
        '1000x400',
        allow_fullsize=False,
        verbose_name="Beskjæring"
    )

    class Meta:
        abstract = True

    def get_picture_url(self):
        return 'http://%s%s%s' % (Site.objects.get_current().domain, settings.MEDIA_URL, self.event_picture.name)


class WithFrontPagePicture(models.Model):
    front_picture = models.ImageField(
        upload_to="uploads/front_page_pictures",
        null=True,
        blank=True,
        verbose_name="Forsidebilde",
        help_text="Bilder som er større enn 250x250 px og er kvadratiske ser best ut. Du kan beskjære bildet etter opplasting."
    )

    front_cropping = ImageRatioField(
        'front_picture',
        '250x250',
        allow_fullsize=False,
        verbose_name="Beskjæring"
    )

    class Meta:
        abstract = True

    def get_front_picture_url(self):
        return 'http://%s%s%s' % (Site.objects.get_current().domain, settings.MEDIA_URL, self.front_picture.name)


class Event(AbstractEvent, WithEventPicture, WithFrontPagePicture):
    """Arrangementer både med og uten påmelding.
    Dukker opp som nyheter på forsiden.
    """

    class Meta:
        verbose_name = "arrangement"
        verbose_name_plural = "arrangement"
        permissions = (
            ("administer", "Can administer models"),
        )
        db_table = "content_event"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._prune_queue()
        EventRegistration.objects.update_lists(self)

    @property
    def registrations_manager(self):
        return EventRegistration.get_manager_for(self)

    @property
    def waiting_registrations(self):
        return self.registrations_manager.waiting_ordered()

    @property
    def attending_registrations(self):
        return self.registrations_manager.attending_ordered()

    def free_places(self):
        """Returnerer antall ledige plasser.

        dvs antall plasser som umiddelbart gir brukeren en garantert plass, og ikke bare
        ventelisteplass.
        Returnerer 0 hvis self.places er None.
        """
        try:
            return max(self.places - self.users_attending(), 0)
        except TypeError:
            return 0

    def is_full(self):
        return self.free_places() == 0

    def users_attending(self):
        """Returnerer antall brukere som er påmeldt."""
        return self.attending_registrations.count()

    def users_attending_emails(self):
        """
        :return: List of attending users emails.
        """
        attending = self.attending_registrations
        return [att.user.email for att in attending]

    def users_waiting(self):
        """Returnerer antall brukere som står på venteliste."""
        return self.waiting_registrations.count()

    def percent_full(self):
        """Returnerer hvor mange prosent av plassene som er tatt."""
        try:
            return min(self.users_attending() * 100 / int(self.places), 100)
        except TypeError:
            return 0
        except ZeroDivisionError:
            return 100

    def is_registered(self, user):
        return self.eventregistration_set.filter(user=user).exists()

    def is_attending(self, user):
        return self.attending_registrations.filter(user=user).exists()

    def is_waiting(self, user):
        return self.waiting_registrations.filter(user=user).exists()

    def get_attendance_list(self):
        return [e.user for e in self.attending_registrations]

    def get_waiting_list(self):
        return [e.user for e in self.waiting_registrations]

    def register_user(self, user):
        """Forsøker å melde brukeren på arrangementet."""
        self._assert_user_allowed_to_register(user)
        return self.add_to_attending_or_waiting_list(user)

    def add_to_attending_or_waiting_list(self, user):
        if self.eventregistration_set.filter(user=user).exists():
            raise RegistrationAlreadyExists(event=self, user=user)

        if not self.is_full():
            return EventRegistration.objects.create_attending_registration(event=self, user=user)
        elif self.has_queue:
            return EventRegistration.objects.create_waiting_registration(event=self, user=user)
        else:
            raise EventFullException(event=self, user=user)

    def deregister_user(self, user):
        """Melder brukeren av arrangementet."""
        if self.deregistration_closed():
            raise DeregistrationClosed(event=self, user=user)
        self.force_deregister_user(user)

    def force_deregister_user(self, user):
        regs = self.eventregistration_set
        try:
            reg = regs.get(user=user)
            reg.delete()
        except EventRegistration.DoesNotExist:
            logger = logging.getLogger(__name__)
            logger.info('Attempt to deregister user from non-existent event.')

    def _prune_queue(self):
        """Sletter overflødige registreringer."""
        if not self.registration_required:
            self.eventregistration_set.all().delete()
        elif not self.has_queue:
            self.waiting_registrations.delete()

    def get_registration_url(self):
        return reverse('registration', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse("event_detail", kwargs={'pk': self.pk, 'slug': self.slug})

    def set_paid_user(self, user):
        reg = self.eventregistration_set.get(user=user)
        reg.set_has_paid()

    def has_paid(self, user):
        return self.eventregistration_set.filter(user=user, has_paid=True).exists()

    def get_place(self, user):
        if self.eventregistration_set.filter(user=user).exists():
            return self.eventregistration_set.get(user=user).number
        else:
            return False

    def send_ticket(self, user):
        reg = self.eventregistration_set.get(user=user)
        reg.send_ticket()
        reg.has_received_ticket = True
        reg.save()
