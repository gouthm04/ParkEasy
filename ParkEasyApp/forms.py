# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



from django import forms
from .models import ParkingSpace

class ParkingSpaceForm(forms.ModelForm):
    class Meta:
        model = ParkingSpace
        fields = ['location', 'price_per_hour', 'availability', 'amenities']
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price per hour'}),
            'availability': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter amenities (optional)', 'rows': 3}),
        }
        labels = {
            'location': 'Parking Space Location',
            'price_per_hour': 'Price per Hour',
            'availability': 'Available for Booking',
            'amenities': 'Amenities (Optional)',
        }

    def clean_price_per_hour(self):
        price = self.cleaned_data.get('price_per_hour')
        if price <= 0:
            raise forms.ValidationError("Price per hour must be greater than zero.")
        return price
