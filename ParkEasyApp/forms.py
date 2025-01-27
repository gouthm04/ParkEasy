from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware
from datetime import datetime
from decimal import Decimal, InvalidOperation
from .models import ParkingSpace, Booking


# Custom user registration form
class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email','password']


# Parking Space form for adding and editing parking spaces
from django import forms
from .models import ParkingSpace
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError


class ParkingSpaceForm(forms.ModelForm):
    class Meta:
        model = ParkingSpace
        fields = ['name', 'location', 'price_per_hour', 'availability', 'amenities', 'longitude', 'latitude', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter parking space name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price per hour'}),
            'availability': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter amenities (optional)', 'rows': 3}),
        }
        labels = {
            'name': 'Parking Space Name',
            'location': 'Parking Space Location',
            'price_per_hour': 'Price per Hour',
            'availability': 'Available for Booking',
            'amenities': 'Amenities (Optional)',
            'image': 'Parking Space Image',
        }


    def clean_price_per_hour(self):
        price = self.cleaned_data.get('price_per_hour')
        if price is None or price == "":
            raise ValidationError("Price per hour cannot be empty.")
        try:
            price = Decimal(price)
            if price <= 0:
                raise ValidationError("Price per hour must be greater than zero.")
        except (ValueError, InvalidOperation):
            raise ValidationError("Enter a valid decimal number for the price.")
        return price



from django import forms
from .models import Booking
from datetime import datetime
from django.utils.timezone import make_aware
from decimal import Decimal

class BookingForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    
    class Meta:
        model = Booking
        fields = ['start_date', 'start_time', 'end_date', 'end_time']

    def __init__(self, *args, user=None, parking_space=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.parking_space = parking_space

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_date = cleaned_data.get('end_date')
        end_time = cleaned_data.get('end_time')

        if start_date and start_time and end_date and end_time:
            start_datetime = make_aware(datetime.combine(start_date, start_time))
            end_datetime = make_aware(datetime.combine(end_date, end_time))

            if start_datetime >= end_datetime:
                raise forms.ValidationError("End time must be after the start time.")

            duration_in_hours = (end_datetime - start_datetime).total_seconds() / 3600
            price_per_hour = Decimal(self.parking_space.price_per_hour)
            total_price = round(Decimal(duration_in_hours) * price_per_hour, 2)
            cleaned_data['price_paid'] = total_price

        return cleaned_data






# Form to edit user details
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'is_active', 'is_superuser']


# forms.py
from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating','comment']