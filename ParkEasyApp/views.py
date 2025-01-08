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

# Check if the user is a superuser
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

# Login view
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Check if the user is a superuser (admin)
            if user.is_superuser:
                return redirect('admin_dashboard')  # Redirect to admin dashboard
            else:
                return redirect('dashboard')  # Redirect to normal user's dashboard
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




# Parking Space List View
def parking_space_list_view(request):
    query = request.GET.get('q', '')
    parking_spaces = ParkingSpace.objects.filter(
        Q(location__icontains=query) & Q(availability=True) & ~Q(host__user=request.user)
    ).order_by('-created_at')
    return render(request, 'parking_space_list.html', {'parking_spaces': parking_spaces, 'query': query})

# Parking Space Detail View
def parking_space_detail_view(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id)
    # Pass the user's ownership status for frontend validation
    is_host = request.user.is_authenticated and parking_space.host == request.user.parkeasyuser
    return render(request, 'parking_space_detail.html', {
        'parking_space': parking_space,
        'is_host': is_host,
    })

# Add Parking Space View
@login_required
def add_parking_space_view(request):
    if request.method == 'POST':
        print(request.POST)
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        form = ParkingSpaceForm(request.POST)
        if form.is_valid():
            parking_space = form.save(commit=False)
            parking_space.host = request.user.parkeasyuser
            parking_space.latitude = latitude 
            parking_space.longitude = longitude 
            parking_space.save()
            return redirect('my_listed_parking_spaces')
    else:
        form = ParkingSpaceForm()
    return render(request, 'add_parking_space.html', {'form': form})

# Edit Parking Space View
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
    return render(request, 'edit_parking_space.html', {
        'form': form,
        'parking_space': parking_space,
    })

# Delete Parking Space View
@login_required
def delete_parking_space_view(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id, host=request.user.parkeasyuser)
    if request.method == 'POST':
        parking_space.delete()
        return redirect('parking_space_list')
    return render(request, 'delete_parking_space.html', {
        'parking_space': parking_space,
    })

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


# BOOKING VIEWS

from django.utils.timezone import make_aware, get_current_timezone
from django.contrib import messages
from .models import ParkingSpace, Booking, ParkEasyUser
from .forms import BookingForm

@login_required
def create_booking_view(request, parking_space_id):
    parking_space = get_object_or_404(ParkingSpace, id=parking_space_id)
    park_easy_user = ParkEasyUser.objects.get(user=request.user)

    if parking_space.host == park_easy_user:
        messages.error(request, "You cannot book your own parking space.")
        return redirect('parking_space_list')

    if request.method == 'POST':
        form = BookingForm(request.POST, user=park_easy_user, parking_space=parking_space)
        print("Form Data:", request.POST)  # Debug form data
        print("Form Valid:", form.is_valid())  # Debug form validity
        if form.is_valid():
            booking = form.save(commit=False)
            booking.parking_space = parking_space
            booking.user = park_easy_user
            booking.save()
            messages.success(request, "Booking created successfully!")
            return redirect('booking_success')
        else:
            print("Form Errors:", form.errors)  # Debug form errors
    else:
        form = BookingForm()

    return render(request, 'create_booking.html', {'form': form, 'parking_space': parking_space})


@login_required
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


from django.utils.timezone import now
from django.db.models import Sum
import json

def earnings_view(request):
    total_earnings = Booking.objects.aggregate(total=Sum('price_paid'))['total']
    current_year = now().year

    monthly_earnings = []
    for month_offset in range(6):  
        month = (now().month - 1 - month_offset) % 12 + 1
        year = current_year if now().month - 1 - month_offset >= 0 else current_year - 1

        earnings = Booking.objects.filter(
            booking_time__year=year,
            booking_time__month=month
        ).aggregate(total=Sum('price_paid'))['total']
        
        monthly_earnings.append(float(earnings) if earnings else 0.0)

    earnings_data = json.dumps(monthly_earnings)

    context = {
        'earnings_data': earnings_data,
        'total_earnings': float(total_earnings) if total_earnings else 0.0,
        'monthly_earnings': sum(monthly_earnings) or 0.0,
    }
    
    return render(request, 'view_earnings.html', context)


def map(request,space_id):
    space=get_object_or_404(ParkingSpace,id=space_id)
    context = {
        'latitude': space.latitude,
        'longitude': space.longitude
    }
    return render(request, 'map.html', context)


# Admin Dash

from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db import models
from .models import ParkingSpace, Booking, ParkEasyUser, Payment, Review, Notification

# Check if the user is a superuser
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser)
def admin_dashboard(request):
    total_users = User.objects.count()
    total_parking_spaces = ParkingSpace.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(status='Completed').aggregate(total_revenue=models.Sum('price_paid'))['total_revenue'] or 0
    
    context = {
        'total_users': total_users,
        'total_parking_spaces': total_parking_spaces,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
    }
    
    return render(request, 'admin_dashboard.html', context)


@user_passes_test(is_superuser)
def manage_users(request):
    users = User.objects.all()
    return render(request, 'manage_users.html', {'users': users})

@user_passes_test(is_superuser)
def manage_parking_spaces(request):
    parking_spaces = ParkingSpace.objects.all()
    return render(request, 'manage_parking_spaces.html', {'parking_spaces': parking_spaces})

@user_passes_test(is_superuser)
def manage_bookings(request):
    bookings = Booking.objects.all()
    return render(request, 'manage_bookings.html', {'bookings': bookings})

@user_passes_test(is_superuser)
def reports(request):
    # Generate reports data here
    return render(request, 'reports.html', {})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .forms import UserEditForm  # Create this form in forms.py if needed

@user_passes_test(is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        # Handle the form submission and update user
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('manage_users')  # Redirect to user management after edit
    else:
        # If not POST, render the form with existing user data
        form = UserEditForm(instance=user)
    
    return render(request, 'edit_user.html', {'form': form, 'user': user})


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User

@user_passes_test(is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()  # Delete the user permanently
    return redirect('manage_users')  # Redirect back to the manage users page

