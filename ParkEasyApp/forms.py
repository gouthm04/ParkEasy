from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import datetime
from .models import ParkingSpace, Booking

# Custom user registration form
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Parking Space form for adding and editing parking spaces
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


# In forms.py
from django import forms
from .models import Booking
from django.utils import timezone
from django.forms.widgets import DateInput, TimeInput
from datetime import datetime

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date', 'start_time', 'end_date', 'end_time', 'price_paid', 'payment_method']

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pop the 'user' argument if passed
        super().__init__(*args, **kwargs)
        if user:
            self.instance.user = user  # Set the user for the instance if provided

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_date = cleaned_data.get('end_date')
        end_time = cleaned_data.get('end_time')

        if start_date and start_time and end_date and end_time:
            # Combine the start and end date/time into datetime objects
            start_datetime = timezone.make_aware(datetime.combine(start_date, start_time), timezone.get_current_timezone())
            end_datetime = timezone.make_aware(datetime.combine(end_date, end_time), timezone.get_current_timezone())

            # Ensure start time is before end time
            if start_datetime >= end_datetime:
                raise forms.ValidationError("End time must be after the start time.")

            # Calculate duration (duration is the time difference between start and end)
            duration = end_datetime - start_datetime
            cleaned_data['duration'] = duration

        return cleaned_data
