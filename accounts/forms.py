from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from .models import User, Profile

class SignupForm(UserCreationForm):
    bio = forms.CharField(required=False)
    website_url = forms.URLField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators = [validate_email]
        self.fields['username'].help_text = '이메일 형식을 입력하세요.'
        self.fields['username'].label = 'Email'

    def save(self):
        user = super().save(commit=False)
        user.email = user.username
        user.save()
        
        bio = self.cleaned_data.get('bio', None)
        website_url = self.cleaned_data.get('website_url', None)

        Profile.objects.create(user=user, bio=bio, website_url=website_url)

        return user

    class Meta(UserCreationForm.Meta):
        model = User
        fileds = UserCreationForm.Meta.fields + ('bio', 'website_url')

    # clean_필드명으로 구현
    """
    def clean_username(self):
        value = self.cleaned_data.get('username')
        if value:
            validate_email(value)
        return
    """

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'website_url']
