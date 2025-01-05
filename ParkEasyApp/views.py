from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import ParkEasyUser, ParkingSpace, Booking
from .forms import CustomUserCreationForm, ParkingSpaceForm, BookingForm
from datetime import timedelta
from django.db.models import Q
from django.utils.timezone import make_aware



# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after login
        messages.error(request, "Invalid username or password")
    return render(request, 'login.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

# Registration View
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            ParkEasyUser.objects.create(user=user)
            messages.success(request, 'Your account has been created successfully! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Profile View
@login_required
def profile_view(request):
    if request.method == "POST":
        user = request.user
        # Update email
        if 'email' in request.POST:
            user.email = request.POST['email']
            user.save()
        
        # Update role
        if 'role' in request.POST:
            role = request.POST['role']
            if role in ['driver', 'host', 'both']:
                park_easy_user = ParkEasyUser.objects.get(user=user)
                park_easy_user.role = role
                park_easy_user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    
    return render(request, 'profile.html')

# Parking Space Views
def parking_space_list_view(request):
    query = request.GET.get('q', '')
    parking_spaces = ParkingSpace.objects.filter(
        Q(location__icontains=query) & Q(availability=True)
    ).order_by('-created_at')
    return render(request, 'parking_space_list.html', {'parking_spaces': parking_spaces, 'query': query})

def parking_space_detail_view(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id)
    return render(request, 'parking_space_detail.html', {'parking_space': parking_space})

@login_required
def add_parking_space_view(request):
    if request.method == 'POST':
        form = ParkingSpaceForm(request.POST)
        if form.is_valid():
            parking_space = form.save(commit=False)
            parking_space.host = request.user.parkeasyuser  # Link the logged-in user as the host
            parking_space.save()
            return redirect('parking_space_list')
    else:
        form = ParkingSpaceForm()
    return render(request, 'add_parking_space.html', {'form': form})

@login_required
def edit_parking_space_view(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id, host=request.user.parkeasyuser)
    if request.method == 'POST':
        form = ParkingSpaceForm(request.POST, instance=parking_space)
        if form.is_valid():
            form.save()
            return redirect('parking_space_detail', space_id=space_id)
    else:
        form = ParkingSpaceForm(instance=parking_space)
    return render(request, 'edit_parking_space.html', {'form': form, 'parking_space': parking_space})

@login_required
def delete_parking_space_view(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id, host=request.user.parkeasyuser)
    if request.method == 'POST':
        parking_space.delete()
        return redirect('parking_space_list')
    return render(request, 'delete_parking_space.html', {'parking_space': parking_space})

# Dashboard and Other Views
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def dashboard(request):
    user_name = request.user.username if request.user.is_authenticated else "Guest"
    return render(request, 'dashboard.html', {"user_name": user_name})

@login_required
def my_listed_parking_spaces(request):
    user_profile = ParkEasyUser.objects.get(user=request.user)
    parking_spaces = ParkingSpace.objects.filter(host=user_profile)
    if not parking_spaces:
        return render(request, 'my_listed_parking_spaces.html', {'message': 'You haven\'t listed any parking spaces yet.'})
    return render(request, 'my_listed_parking_spaces.html', {'parking_spaces': parking_spaces})

def help_support(request):
    return render(request, 'help_support.html')

def faq(request):
    return render(request, 'FAQ_Page.html')

def terms_conditions(request):
    return render(request, 'terms_conditions.html')


# Booking Views
from datetime import timedelta
from datetime import datetime
from django.utils import timezone  # <-- Add this import
from django.utils.timezone import make_aware


@login_required
def create_booking_view(request, parking_space_id):
    parking_space = get_object_or_404(ParkingSpace, id=parking_space_id)
    park_easy_user = ParkEasyUser.objects.get(user=request.user)

    if request.method == 'POST':
        form = BookingForm(request.POST, user=park_easy_user)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            start_date = cleaned_data['start_date']
            start_time = cleaned_data['start_time']
            end_date = cleaned_data['end_date']
            end_time = cleaned_data['end_time']

            # Combine date and time into datetime objects
            start_datetime = make_aware(datetime.combine(start_date, start_time), timezone.get_current_timezone())
            end_datetime = timezone.make_aware(datetime.combine(end_date, end_time), timezone.get_current_timezone())

            # Check if a booking already exists for the same parking space and time range
            existing_booking = Booking.objects.filter(
                parking_space=parking_space,
                start_date__lt=end_date,  # Use start_date and end_date here
                end_date__gt=start_date   # Use end_date and start_date
            ).exists()

            if existing_booking:
                # Handle the conflict (e.g., show an error message)
                form.add_error(None, "A booking already exists for this parking space during the selected time.")
            else:
                # Calculate the duration
                duration = end_datetime - start_datetime

                price_paid = cleaned_data.get('price_paid', 0.0)
                payment_method = cleaned_data.get('payment_method', 'Unknown')

                # Create the booking instance
                booking = form.save(commit=False)
                booking.start_datetime = start_datetime
                booking.end_datetime = end_datetime
                booking.parking_space = parking_space
                booking.user = park_easy_user
                booking.price_paid = price_paid
                booking.payment_method = payment_method
                booking.duration = duration  # Set the duration
                booking.save()

                return redirect('booking_success')  # Replace with your actual success URL
        else:
            # Log form errors if form is not valid
            logger.debug("Form is not valid.")
            logger.debug(form.errors)
    else:
        form = BookingForm(user=park_easy_user)

    return render(request, 'create_booking.html', {'form': form, 'parking_space': parking_space})



# views.py
from django.shortcuts import render

def booking_success_view(request):
    return render(request, 'booking_success.html')


@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_detail.html', {'booking': booking})

@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user.parkeasyuser)
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('dashboard')
    return render(request, 'cancel_booking.html', {'booking': booking})


from django.core.paginator import Paginator

@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user.parkeasyuser)
    paginator = Paginator(bookings, 10)  # Show 10 bookings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'my_bookings.html', {'page_obj': page_obj})


