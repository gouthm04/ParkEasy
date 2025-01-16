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
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.db.models import Sum
import json
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from .forms import UserEditForm  # Import the form




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
            if user.is_superuser:
                return redirect('admin_dashboard')  # Redirect to admin dashboard
            else:
                return redirect('dashboard')  # Redirect to normal user's dashboard
        messages.error(request, "Invalid username or password")
    return render(request, 'auth/login.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

# Registration View
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user instance
            user = form.save()

            # Check if a ParkEasyUser entry already exists for the user
            parkeasy_user, created = ParkEasyUser.objects.get_or_create(user=user)

            if created:  # Entry was created successfully
                messages.success(request, 'Your account has been created successfully! You can now log in.')
            else:  # Entry already exists (should not normally happen in registration)
                messages.warning(request, 'This user already exists.')

            return redirect('login')
    else:
        return render(request, 'auth/register.html')


# Profile View
@login_required
def profile_view(request):
    if request.method == "POST":
        user = request.user
        if 'email' in request.POST:
            user.email = request.POST['email']
            user.save()
        if 'role' in request.POST:
            role = request.POST['role']
            if role in ['driver', 'host', 'both']:
                park_easy_user = ParkEasyUser.objects.get(user=user)
                park_easy_user.role = role
                park_easy_user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    
    return render(request, 'auth/profile.html')

# Parking Space List View
from django.db.models import Q
from django.shortcuts import render
from .models import ParkingSpace

def parking_space_list_view(request):
    query = request.GET.get('q', '')
    parking_spaces = ParkingSpace.objects.filter(
        Q(location__icontains=query) & Q(availability=True) & ~Q(host__user=request.user)
    ).order_by('-created_at')
    
    # Render the template with the filtered parking spaces and the query
    return render(request, 'parking/parking_space_list.html', {
        'parking_spaces': parking_spaces,
        'query': query
    })


# Parking Space Detail View
def parking_space_detail_view(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id)
    is_host = request.user.is_authenticated and parking_space.host == request.user.parkeasyuser
    return render(request, 'parking/parking_space_detail.html', {
        'parking_space': parking_space,
        'is_host': is_host,
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ParkingSpace
from .forms import ParkingSpaceForm  # Import the form here
from django.shortcuts import get_object_or_404
from ParkEasyApp.models import ParkEasyUser, ParkingSpace

@login_required
def add_parking_space_view(request):
    if request.method == 'POST':
        form = ParkingSpaceForm(request.POST)
        if form.is_valid():
            user = request.user
            parkeasy_user = get_object_or_404(ParkEasyUser, user=user)
            parking_space = form.save(commit=False)
            parking_space.host = parkeasy_user
            parking_space.save()
            return redirect('success_url')  # Replace with your success URL
    else:
        form = ParkingSpaceForm()

    return render(request, 'parking/add_parking_space.html', {'form': form})



from django.shortcuts import render
def success_view(request):
    return render(request, 'parking/success.html')  # Ensure you have a 'success.html' template



from django.shortcuts import render, get_object_or_404
from .models import ParkingSpace
def map(request, space_id):
    # Fetch parking space by ID
    space = get_object_or_404(ParkingSpace, id=space_id)
    
    # If latitude or longitude is None, fall back to default coordinates
    latitude = space.latitude if space.latitude else 51.505  # Default value if None
    longitude = space.longitude if space.longitude else -0.09  # Default value if None
    
    context = {
        'latitude': latitude,
        'longitude': longitude,
        'location': space.location,  # Location name to show
    }
    
    return render(request, 'map/map.html', context)




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
    return render(request, 'parking/edit_parking_space.html', {
        'form': form,
        'parking_space': parking_space,
    })

# Delete Parking Space View
@login_required
def delete_parking_space_view(request, space_id):
    try:
        parkeasy_user = request.user.parkeasyuser
    except ParkEasyUser.DoesNotExist:
        parkeasy_user, _ = ParkEasyUser.objects.get_or_create(user=request.user)

    parking_space = get_object_or_404(ParkingSpace, id=space_id, host=parkeasy_user)
    if request.method == 'POST':
        parking_space.delete()
        return redirect('my_listed_parking_spaces')
    return render(request, 'parking/delete_parking_space.html', {'parking_space': parking_space})


# Dashboard and Other Views
def home(request):
    return render(request, 'user/home.html')

def about(request):
    return render(request, 'pages/about.html')

def contact(request):
    return render(request, 'contact.html')

def dashboard(request):
    user_name = request.user.username if request.user.is_authenticated else "Guest"
    return render(request, 'user/dashboard.html', {"user_name": user_name})

@login_required
def my_listed_parking_spaces(request):
    user_profile = ParkEasyUser.objects.get(user=request.user)
    parking_spaces = ParkingSpace.objects.filter(host=user_profile)
    if not parking_spaces:
        return render(request, 'parking/my_listed_parking_spaces.html', {'message': 'You haven\'t listed any parking spaces yet.'})
    return render(request, 'parking/my_listed_parking_spaces.html', {'parking_spaces': parking_spaces})

def help_support(request):
    return render(request, 'pages/help_support.html')

def faq(request):
    return render(request, 'pages/FAQ_Page.html')


def terms_conditions(request):
    return render(request, 'pages/terms_conditions.html')




from django.urls import reverse

def create_booking_view(request, parking_space_id):
    # Fetch parking space and user
    parking_space = ParkingSpace.objects.get(id=parking_space_id)
    
    try:
        parkeasy_user = ParkEasyUser.objects.get(user=request.user)
    except ParkEasyUser.DoesNotExist:
        messages.error(request, "User profile is incomplete. Please contact support.")
        return redirect('profile')

    form = BookingForm(request.POST or None, user=parkeasy_user, parking_space=parking_space)

    if form.is_valid():
        cleaned_data = form.cleaned_data
        start_datetime = cleaned_data['start_datetime']
        end_datetime = cleaned_data['end_datetime']

        # Check for conflicts
        conflicting_booking = Booking.objects.filter(
            parking_space=parking_space,
            end_date__gte=start_datetime.date(),
            end_time__gte=start_datetime.time(),
            start_date__lte=end_datetime.date(),
            start_time__lte=end_datetime.time()
        ).exists()

        if conflicting_booking:
            form.add_error(None, "The parking space is already booked for the selected time.")
        else:
            # Save a tentative booking
            booking = form.save(commit=False)
            booking.parking_space = parking_space
            booking.user = parkeasy_user
            booking.status = "tentative"  # Example status for incomplete payment
            booking.save()

            # Redirect to payment form with booking ID
            # In your payment_form_view
            payment_url = reverse('payment_form')  # Ensure reverse() works correctly
            print(f"Redirecting to: {payment_url}?booking_id={booking.id}")
            return redirect(f"{payment_url}?booking_id={booking.id}")


    return render(request, 'booking/create_booking.html', {
        'parking_space': parking_space,
        'form': form
    })


from django.shortcuts import render

@login_required
def booking_success_view(request):
    booking_id = request.GET.get('booking_id')
    booking = None
    if booking_id:
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            booking = None

    return render(request, 'booking/booking_success.html', {'booking': booking})





@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking/booking_detail.html', {'booking': booking})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking

@login_required
def cancel_booking_view(request, booking_id):
    # Fetch the booking object for the logged-in user
    booking = get_object_or_404(Booking, id=booking_id, user=request.user.parkeasyuser)
    
    if request.method == 'POST':
        # Mark the booking as cancelled and delete it
        booking.delete()
        messages.success(request, "Booking cancelled and removed successfully.")
        return redirect('my_bookings')  # Redirect back to my bookings page
    
    return render(request, 'booking/cancel_booking.html', {'booking': booking})


from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Booking

@login_required
def my_bookings_view(request):
    # Fetch all bookings of the logged-in user
    bookings = Booking.objects.filter(user=request.user.parkeasyuser)
    
    # Paginate the bookings list (10 bookings per page)
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Render the template with the page_obj to handle pagination and booking data
    return render(request, 'booking/my_bookings.html', {'page_obj': page_obj})



# Earnings View
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
    
    return render(request, 'admin/view_earnings.html', context)












# Admin Dashboard Views
@user_passes_test(is_superuser)
def admin_dashboard(request):
    total_users = User.objects.count()
    total_parking_spaces = ParkingSpace.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(status='Completed').aggregate(total_revenue=Sum('price_paid'))['total_revenue'] or 0
    
    context = {
        'total_users': total_users,
        'total_parking_spaces': total_parking_spaces,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
    }
    
    return render(request, 'admin/admin_dashboard.html', context)

@user_passes_test(is_superuser)
def manage_users(request):
    users = User.objects.all()
    return render(request, 'admin/manage_users.html', {'users': users})

@user_passes_test(is_superuser)
def manage_parking_spaces(request):
    parking_spaces = ParkingSpace.objects.all()
    return render(request, 'admin/manage_parking_spaces.html', {'parking_spaces': parking_spaces})

from django.shortcuts import render
from .models import Booking
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(is_superuser)
def manage_bookings(request):
    bookings = Booking.objects.all()
    return render(request, 'admin/manage_bookings.html', {'bookings': bookings})



@user_passes_test(is_superuser)
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)  # Fetch booking by ID
    # Handle your form submission or editing logic here

    return render(request, 'edit_booking.html', {'booking': booking})


@user_passes_test(is_superuser)
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.delete()  # Delete the booking object
        return redirect('manage_bookings')  # Redirect to the bookings management page
    return render(request, 'delete_booking_confirmation.html', {'booking': booking})  # Optional: Show confirmation page



@user_passes_test(is_superuser)
def reports(request):
    return render(request, 'admin/reports.html', {})
@user_passes_test(is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User details updated successfully.")  # Feedback to admin
            return redirect('manage_users')
        else:
            messages.error(request, "Failed to update user details. Please check the form.")
    else:
        form = UserEditForm(instance=user)

    return render(request, 'admin/edit_user.html', {'form': form, 'user': user})


import logging

logger = logging.getLogger(__name__)  # Set up logging

@user_passes_test(is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.delete()
        messages.success(request, f"User '{user.username}' deleted successfully.")
        logger.info(f"User '{user.username}' (ID: {user.id}) was deleted by admin {request.user.username}.")
        return redirect('manage_users')
    return render(request, 'admin/confirm_delete_user.html', {'user': user})


# PAYMENT 
def payment_form_view(request):
    booking_id = request.GET.get('booking_id')

    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        messages.error(request, "Invalid booking. Please try again.")
        return redirect('home')

    if request.method == "POST":
        # Handle payment processing logic here
        payment_method = request.POST.get('payment_method')

        if payment_method:  # Assume payment is successful for now
            booking.status = "confirmed"
            booking.save()
            messages.success(request, "Payment successful! Booking confirmed.")
            return redirect('booking_success')

        messages.error(request, "Payment failed. Please try again.")
    
    return render(request, 'payment_form.html', {'booking': booking})
