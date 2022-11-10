from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy

from . import views

urlpatterns = [
    # innlogging og registrering
    url(r'^logg-inn/$', auth_views.login, {'template_name': 'user_login.html', 'redirect_authenticated_user': True}, name='user.login'),
    url(r'^logg-ut/$', auth_views.logout, {'next_page': '/'}, name='user.logout'),
    url(r'^registrer-meg/$', views.registration, name='user.registration'),
    # glemt passord relatert
    url(r'^glemt-passord/$', auth_views.PasswordResetView.as_view(template_name='password_reset/user_password_reset.html', email_template_name='password_reset/user_password_reset_email.html', subject_template_name='password_reset/user_password_reset_subject.txt', success_url=reverse_lazy('user.reset_done'), from_email='ikke-svar@nabla.no'),
        name='user.reset'),
    url(r'^glemt-passord/epost-sendt/$', auth_views.PasswordResetDoneView.as_view(template_name='password_reset/user_password_reset_done.html'),
        name='user.reset_done'),
    url(r'^nytt-passord/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset/user_password_reset_confirm.html', success_url=reverse_lazy('user.reset_confirm_done')),
        name='user.reset_confirm'),
    url(r'^nytt-passord/lagret/$', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/user_password_reset_complete.html'),
        name='user.reset_confirm_done'),
    # bruker - forside relatert
    url(r'^min-profil/$', views.profile, name='user.profile'),
    # bruker - innstillings relatert
    url(r'^min-profil/innstillinger/$', views.settings, name='user.settings'),
    url(r'^min-profil/innstillinger/endre-informasjon/$', views.profileUpdate, name='user.update'),
    url(r'^min-profil/innstillinger/endre-passord/$', auth_views.PasswordChangeView.as_view(template_name='settings/user_password_change.html', success_url=reverse_lazy('user.change_password_done')),
        name='user.change_password'),
    url(r'^min-profil/innstillinger/endre-passord/endret/$', auth_views.PasswordChangeView.as_view(template_name='settings/user_password_change_done.html'),
        name='user.change_password_done'),
    # bruker - arrangement relatert
    url(r'^min-profil/arrangementer/$', views.events, name='user.events'),
    # bruker - administrasjonsrelatert
    url(r'^min-profil/brukere/$', views.registerapplicants, name='user.registerapplicants'),
    url(r'^min-profil/brukere/(?P<action>accept|undecided|decline|delete)/(?P<userid>[0-9]+)/', views.changeapplicants, name='user.changeapplicants'),
    url(r'brukerseed/',
        views.InjectUsersFormView.as_view(),
        name='users_inject')
]