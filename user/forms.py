from .models import User
from django import forms
from django.core.validators import RegexValidator


class RegistrationForm(forms.ModelForm):

    numeric_only = RegexValidator(regex='[0-9]+', message='Only numbers are allowed.', code='Invalid number.')
    spam_bot_validator = RegexValidator(regex='[2]', message='Try to calculate again :)', code='Try to calculate again :)')

    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '*********', 'required': 'true'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'smart@nobel.de', 'required': 'true'}))
    first_name = forms.CharField(max_length=80, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Albert', 'required': 'true'}))
    last_name = forms.CharField(max_length=80, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Einstein', 'required': 'true'}))
    starting_year = forms.CharField(validators=[numeric_only], required=True, max_length=4, min_length=4, widget=forms.TextInput(attrs={'class': 'form-control', 'pattern':'[0-9]{4}', 'placeholder': '1896 (året du begynte på fysmat/kullet du fulgte)', 'required': 'true'}))
    allergies = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Allergier'}))
    spam_bot_check = forms.IntegerField(required=True, validators=[spam_bot_validator], widget=forms.TextInput(attrs={'class': 'git form-control', 'placeholder': 'Svaret på oppgaven', 'required': 'true'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'starting_year', 'allergies']

class UpdateUserForm(forms.ModelForm):
    numeric_only = RegexValidator(regex='[0-9]+', message='Only numbers are allowed.', code='Invalid number.')
    first_name = forms.CharField(max_length=80, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Albert'}))
    last_name = forms.CharField(max_length=80, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Einstein'}))
    starting_year = forms.CharField(validators=[numeric_only], required=False, max_length=4, min_length=4,
                                    widget=forms.TextInput(
                                        attrs={'class': 'form-control', 'pattern': '[0-9]{4}', 'placeholder': '1896'}))
    allergies = forms.CharField(max_length=200, required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Terninger'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'starting_year', 'allergies']

class InjectUsersForm(forms.Form):
    title = "Legg til brukere med følgende emailadresser i databasen."
    data = forms.CharField(
        widget=forms.Textarea,
        label="Data"
    )