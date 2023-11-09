from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Trip

from django import forms

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['departure_location', 'destination', 'departure_time', 'available_seats']
        widgets = {
            'departure_location': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_time': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class RegisterUserForm(UserCreationForm):
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    first_name=forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name=forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))

    class meta:
        model=User
        fields=('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class']='form-control'
        self.fields['password1'].widget.attrs['class']='form-control'
        self.fields['password2'].widget.attrs['class']='form-control'