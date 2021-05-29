from django import forms
from .models import Indexcheck

class IndexCreateForm(forms.ModelForm):

    class Meta:
        model = Indexcheck
        exclude = ('created_at',)
        fields = ('theme_name', 'code')

from django.contrib.auth.forms import UserCreationForm

# ユーザ作成フォームを継承
class SignUpForm(UserCreationForm):
    username = forms.CharField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
