import re
from braces.views import (FormMessagesMixin, LoginRequiredMixin, PermissionRequiredMixin)
from django.http import HttpResponseForbidden
from django.views.generic import FormView
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import RegistrationForm, UpdateUserForm, InjectUsersForm
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from . models import User
from events.models.eventregistration import EventRegistration

# Register user
def registration(request):

    # check if user is already logged in
    if request.user.is_authenticated:
        return redirect('user.profile')

    else:

        # check if post method is being performed
        if request.method == "POST":
            form = RegistrationForm(request.POST)

            # validate form
            if form.is_valid():

                # try to see if a user with the same email is already registered
                try:

                    user = User.objects.get(username=form.cleaned_data['email'])

                except User.DoesNotExist:

                    # create user
                    user = User.objects.create_user(form.cleaned_data['email'],
                                                    form.cleaned_data['email'],
                                                    form.cleaned_data['password'],
                                                    first_name=form.cleaned_data['first_name'],
                                                    last_name=form.cleaned_data['last_name'],
                                                    starting_year=form.cleaned_data['starting_year'],
                                                    allergies=form.cleaned_data['allergies'],
                                                    is_active = False,
                                                    account_verified = False,
                                                    is_awaiting_approval = True
                                                    )
                    user.save()

                    # redirect with success message
                    return redirect(reverse('user.registration') + '?reg=1')

            else:
                # redirect with error message
                return render(request, 'user_registration.html', {'form': form})

        else:
            form = RegistrationForm()

        # registration completed
        if request.GET.get('reg') == '1':
            done = True
        else:
            done = False

        return render(request, 'user_registration.html', {'form': form, 'done': done})

def profileUpdate(request):

    # check if user is already logged in
    if request.user.is_authenticated:

        # check if post method is being performed
        if request.method == "POST":
            form = UpdateUserForm(request.POST)
            # validate form
            if form.is_valid():
                update = form.save(commit=False)
                if update.first_name:
                    request.user.first_name = update.first_name
                if update.last_name:
                    request.user.last_name = update.last_name
                if update.starting_year:
                    request.user.starting_year = update.starting_year

                # must allow none
                request.user.allergies = update.allergies

                request.user.save()
                # redirect with success message
                return redirect(reverse('user.settings') + '?reg=1')

            else:
                # redirect with error message
                return render(request, 'user_update.html', {'form': form})

        else:
            form = UpdateUserForm(instance=User.objects.get(id=request.user.id))

        # registration completed
        if request.GET.get('reg') == '1':
            done = True
        else:
            done = False

        return render(request, 'user_update.html', {'form': form, 'done': done})

    else:
        raise PermissionDenied


# Recover user password
def recover(request):
    if request.user.is_authenticated:
        return redirect('user.profile')

    else:

        # check if post method is being performed
        if request.method == "POST":
            form = RecoveryForm(request.POST)

            # validate form
            if form.is_valid():

                return render(request, 'user_recover.html', {'form': form})

            else:
                # redirect with error message
                return render(request, 'user_recover.html', {'form': form})

        else:
            form = RecoveryForm()

        # recovery email sent
        if request.GET.get('reg') == '1':
            done = True
        else:
            done = False

        return render(request, 'user_recover.html', {'form': form, 'done': done})

# Displays user profile
def profile(request):
    if request.user.is_authenticated:
        return render(request, 'user_profile.html', {'is_authenticated': request.user.is_authenticated})
    else:
        raise PermissionDenied

# Displays user settings
def settings(request):
    if request.user.is_authenticated:
        return render(request, 'user_settings.html')
    else:
        raise PermissionDenied

# Lists all events you have signed up on
def events(request):
    if request.user.is_authenticated:
        attending_events = EventRegistration.objects.all().filter(user=request.user, attending=True).order_by('event__event_start')
        on_waiting_list = EventRegistration.objects.all().filter(user=request.user, attending=False).order_by('event__event_start')
        return render(request, 'user_events.html', {'attending_events': attending_events, 'on_waiting_list': on_waiting_list})
    else:
        raise PermissionDenied

# Lists all users according to different statuses
def registerapplicants(request):
    if request.user.is_authenticated and request.user.has_perm('user.can_view_users'):

        if request.GET.get('msg') == '1':
            message = 'Brukeren har blitt godkjent og kan nå logge inn. En e-post bekreftelse har blitt sendt til vedkommende.'
        elif request.GET.get('msg') == '2':
            message = 'Brukeren har blitt tilbakeført til avventende og kan ikke logge inn. Ingen e-post har blitt sendt ut til vedkommende.'
        elif request.GET.get('msg') == '3':
            message = 'Brukeren har blitt avvist, og kan ikke logge inn. E-post er sendt til vedkommende.'
        elif request.GET.get('msg') == '3':
            message = 'Brukeren er slettet. Ingen e-post er sendt ut til vedkommende.'
        else:
            message = None

        if request.GET.get('list') == 'accepted':

            # get all accepted users in user list
            user_list = User.objects.filter(is_awaiting_approval=False, is_active=True)
            user_title = 'Godkjente brukere'

        elif request.GET.get('list') == 'declined':

            # get all declined users in user list
            user_list = User.objects.filter(is_awaiting_approval=False, is_staff=False, is_active=False)
            user_title = 'Avslåtte brukere'

        else:

            # get all users awaiting checkup
            user_list = User.objects.filter(is_awaiting_approval=True, is_staff=False)
            user_title = 'Brukere som avventer godkjenning'

        return render(request, 'user_registerapplicants.html', {'user_list': user_list, 'user_title': user_title, 'message': message})
    else:
        raise PermissionDenied

# Change the user status for registration
def changeapplicants(request, action, userid):
    if request.user.is_authenticated and request.user.has_perm('user.can_change_users'):

        if action == 'accept':

            # update user to accepted, and change status to has been checked
            user = User.objects.get(id=userid, is_staff=False, is_active=False)
            user.is_awaiting_approval = False
            user.is_active = True
            user.save(update_fields=["is_awaiting_approval", "is_active"])

            # send email regarding accepted user
            send_mail("Du har blitt godkjent", "Din bruker på https://jubileum.nabla.no har blitt godkjent. Du kan nå logge inn.", 'noreply@nabla.no', [user.email])

            # redirect to register applicants with msg = 1 (meaning approved)
            return redirect(reverse('user.registerapplicants') + '?msg=1')

        elif action == 'undecided':

            # update user to awaiting checkup and inactive
            user = User.objects.get(id=userid, is_staff=False, is_active=False, is_awaiting_approval=False)
            user.is_awaiting_approval = True
            user.is_active = False
            user.save(update_fields=["is_awaiting_approval", "is_active"])

            # redirect to register applicants with msg = 2 (meaning undecided)
            return redirect(reverse('user.registerapplicants') + '?msg=2')

        elif action == 'decline':

            # update user to declined, and change status to has been checked
            user = User.objects.get(id=userid, is_staff=False, is_awaiting_approval=True, is_active=False)
            user.is_awaiting_approval = False
            user.is_active = False
            user.save(update_fields=["is_awaiting_approval", "is_active"])

            # redirect to register applicants with msg = 3 (meaning disapproved)
            return redirect(reverse('user.registerapplicants') + '?msg=3')

        elif action == 'delete':

            # delete user
            user = User.objects.get(id=userid, is_staff=False, is_active=False)
            user.delete()

            # redirect to register applicants with msg = 4 (meaning deleted)
            return redirect(reverse('user.registerapplicants') + '?msg=4')

        else:
            raise PermissionDenied
    else:
        raise PermissionDenied


class InjectUsersFormView(LoginRequiredMixin, PermissionRequiredMixin, FormMessagesMixin, FormView):

    permission_required = "user.add_user"

    form_class = InjectUsersForm
    form_valid_message = "Brukerne er lagt i databasen."
    form_invalid_message = "Ikke riktig utfyllt."
    template_name = 'form.html'
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.has_module_perms("django.contrib.auth"):
            return super(InjectUsersFormView, self).dispatch(request, *args, **kwargs)
        return HttpResponseForbidden()

    def form_valid(self, form):
        data = form.cleaned_data['data']
        extract_usernames(data)
        return super(InjectUsersFormView, self).form_valid(form)

def extract_usernames(string):
    from .models import User

    m = re.findall('([^\s]+)', string, re.IGNORECASE)
    for u in m:
        new_user, was_created = User.objects.get_or_create(email=u)
        if not was_created:
            continue
        new_user.username = u
        new_user.first_name = "Gjestebruker"
        new_user.last_name = str(new_user.id)
        new_user.starting_year = "0000"
        new_user.is_awaiting_approval = False
        new_user.save()
