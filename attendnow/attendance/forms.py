from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required')
    email = forms.EmailField(max_length=254, required=True, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class SignInForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image']


class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture']  # Adjust fields as needed

    profile_picture = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('instance', None)
        super(AccountSettingsForm, self).__init__(*args, **kwargs)
        if not user or not user.is_authenticated:
            # Provide default initialization if needed
            self.fields['username'].required = False
            self.fields['email'].required = False
            self.fields['profile_picture'].required = False


class NotificationSettingsForm(forms.Form):
    email_notifications = forms.BooleanField(required=False)
    sms_notifications = forms.BooleanField(required=False)
    app_notifications = forms.BooleanField(required=False)
    notification_style = forms.ChoiceField(choices=[('silent', 'Silent'), ('alert', 'Alert'), ('banner', 'Banner')])
    notification_volume = forms.IntegerField(min_value=0, max_value=100)
    notification_tone = forms.ChoiceField(choices=[('default', 'Default'), ('beep', 'Beep'), ('chime', 'Chime'), ('alert', 'Alert')])