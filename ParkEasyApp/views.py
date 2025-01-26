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

from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Notification

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Create a ParkEasyUser if needed (assuming you have a ParkEasyUser model)
        ParkEasyUser.objects.create(user=user)
        
        # Create a notification for the admin
        admin_user = User.objects.get(is_superuser=True)  # Assuming the admin is a superuser
        notification_message = f"A new user, {user.username}, has registered."
        Notification.objects.create(
            user=admin_user,
            message=notification_message,
            notification_type='USER_REGISTRATION'
        )

        # Display a success message and redirect to login
        messages.success(request, 'Your account has been created successfully! You can now log in.')
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



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ParkingSpace, Notification
from .forms import ParkingSpaceForm
from ParkEasyApp.models import ParkEasyUser

@login_required
def add_parking_space_view(request):
    if request.method == 'POST':
        form = ParkingSpaceForm(request.POST, request.FILES)  # Add request.FILES here
        if form.is_valid():
            user = request.user
            parkeasy_user = get_object_or_404(ParkEasyUser, user=user)
            parking_space = form.save(commit=False)
            parking_space.host = parkeasy_user
            parking_space.save()

            # Create a notification for the parking host
            Notification.objects.create(
                user=user,
                message=f"Your parking space '{parking_space.name}' has been successfully added and is now available.",
                notification_type='PARKING_AVAILABLE'
            )

            # Create a notification for the admin (assuming admins are superusers)
            admin_users = User.objects.filter(is_superuser=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    message=f"A new parking space '{parking_space.name}' has been created by {user.username}.",
                    notification_type='NEW_PARKING_SPACE'  # You can use the same type or create a new one like 'NEW_PARKING_SPACE'
                )

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



# edit parking space
from django.shortcuts import render, get_object_or_404, redirect
from .models import ParkingSpace
from .forms import ParkingSpaceForm
from django.contrib.auth.decorators import login_required

# Check if the user is a superuser
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@login_required
def edit_parking_space_view(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id)
    
    if request.method == "POST":
        form = ParkingSpaceForm(request.POST, instance=parking_space)
        if form.is_valid():
            parking_space = form.save(commit=False)
            # Update location coordinates
            parking_space.latitude = request.POST.get('latitude')
            parking_space.longitude = request.POST.get('longitude')
            parking_space.save()

            # Check if the user is an admin and redirect accordingly
            if is_superuser(request.user):
                return redirect('manage_parking_spaces')  # Redirect to the parking space management page
            else:
                return redirect('my_listed_parking_spaces')  # Or other redirection if needed (for non-admin users)

    else:
        form = ParkingSpaceForm(instance=parking_space)

    return render(request, 'parking/edit_parking_space.html', {'form': form})




# Delete Parking Space View
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import ParkingSpace, Notification

@login_required
def delete_parking_space_view(request, space_id):
    # Get the ParkEasyUser object for the current user
    parkeasy_user = request.user.parkeasyuser

    # Fetch the parking space to delete
    parking_space = get_object_or_404(ParkingSpace, id=space_id, host=parkeasy_user)

    if request.method == 'POST':
        # Store details for notification before deletion
        parking_space_name = parking_space.name  # Assuming the ParkingSpace model has a 'name' field
        host_username = request.user.username

        # Delete the parking space
        parking_space.delete()

        # Notify the user who deleted their parking space
        Notification.objects.create(
            user=request.user,
            message=f"Your parking space '{parking_space_name}' has been successfully deleted.",
            notification_type='PARKING_DELETED'
        )

        # Notify the admin about the deletion
        admin_user = User.objects.get(is_superuser=True)  # Assuming the admin is a superuser
        Notification.objects.create(
            user=admin_user,
            message=f"Parking space '{parking_space_name}' hosted by {host_username} has been deleted.",
            notification_type='PARKING_DELETED'
        )

        # Display a success message to the user
        messages.success(request, f"Parking space '{parking_space_name}' has been deleted successfully.")
        return redirect('my_listed_parking_spaces')

    return render(request, 'parking/delete_parking_space.html', {'parking_space': parking_space})



# Dashboard and Other Views
def home(request):
    return render(request, 'user/home.html')

def about(request):
    return render(request, 'pages/about.html')

def contact(request):
    return render(request, 'contact.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Notification

@login_required
def dashboard(request):
    # Get notifications for the logged-in user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Get unread notifications
    unread_notifications = notifications.filter(is_read=False)

    # Pass the unread notifications to the template (we don't need to pass count anymore)
    user_name = request.user.username if request.user.is_authenticated else "Guest"
    return render(request, 'user/dashboard.html', {
        'user_name': user_name,
        'unread_notifications': unread_notifications,
        'notifications': notifications
    })

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




from django.shortcuts import render, redirect
from .forms import BookingForm
from .models import ParkingSpace, Booking, Payment, ParkEasyUser
from django.urls import reverse

def create_booking_view(request, parking_space_id):
    parking_space = ParkingSpace.objects.get(id=parking_space_id)
    user = ParkEasyUser.objects.get(user=request.user)  # The driver (user) making the booking
    form = BookingForm(request.POST or None, user=user, parking_space=parking_space)

    if form.is_valid():
        cleaned_data = form.cleaned_data
        price_paid = cleaned_data['price_paid']
        
        # Ensure host is correctly assigned (the parking space's owner)
        host = parking_space.host  # Correct reference to 'host' field
        
        booking = form.save(commit=False)
        booking.parking_space = parking_space
        booking.user = user  # The driver (booking user)
        booking.host = host  # The parking space owner (host) will receive the earnings
        booking.price_paid = price_paid
        booking.status = "booked"
        booking.save()

        # Create payment instance, linked to the booking
        payment = Payment.objects.create(
            booking=booking,
            amount=price_paid,
            payment_status="pending"
        )

        payment_url = reverse('payment_form')
        return redirect(f"{payment_url}?booking_id={booking.id}&price_paid={price_paid}")

    return render(request, 'booking/create_booking.html', {'parking_space': parking_space, 'form': form})







from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import ParkEasyUser, ParkingSpace, Booking
from .forms import BookingForm
from datetime import datetime
from django.utils.timezone import make_aware
from decimal import Decimal
# Booking Success View
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



from django.shortcuts import render
from django.db.models import Sum
from django.utils.timezone import now
import json
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import ParkEasyUser, Booking, Payment

def earnings_view(request):
    user = request.user

    # Fetch the corresponding ParkEasyUser instance for the logged-in user
    parkeasy_user = get_object_or_404(ParkEasyUser, user=user)
    
    # Ensure filtering only the bookings of the logged-in user (parkeasy_user) as a host
    total_earnings = round(Booking.objects.filter(host=parkeasy_user).aggregate(total=Sum('price_paid'))['total'] or 0.0, 2)
    
    # Admin earnings from payments (ensure correct payment object filtering)
    admin_earnings = round(Payment.objects.aggregate(total=Sum('admin_commission'))['total'] or 0.0, 2)
    
    # Current year and month for further calculations
    current_year = now().year
    current_month = now().month

    # Calculate yearly earnings for the current year for the host
    yearly_earnings = round(Booking.objects.filter(
        host=parkeasy_user,
        booking_time__year=current_year
    ).aggregate(total=Sum('price_paid'))['total'] or 0.0, 2)

    # Calculate daily earnings (earnings for today)
    daily_earnings = round(Booking.objects.filter(
        host=parkeasy_user,
        booking_time__date=now().date()
    ).aggregate(total=Sum('price_paid'))['total'] or 0.0, 2)

    # Calculate monthly earnings for the past 6 months for the host
    monthly_earnings = []
    for month_offset in range(6):  
        month = (current_month - 1 - month_offset) % 12 + 1
        year = current_year if current_month - 1 - month_offset >= 0 else current_year - 1

        earnings = Booking.objects.filter(
            host=parkeasy_user,
            booking_time__year=year,
            booking_time__month=month
        ).aggregate(total=Sum('price_paid'))['total']
        
        monthly_earnings.append(round(float(earnings) if earnings else 0.0, 2))

    earnings_data = json.dumps(monthly_earnings)

    # Add all calculated earnings to the context
    context = {
        'total_earnings': total_earnings,
        'admin_earnings': admin_earnings,
        'yearly_earnings': yearly_earnings,
        'daily_earnings': daily_earnings,
        'monthly_earnings': sum(monthly_earnings),
        'earnings_data': earnings_data,
    }
    
    return render(request, 'admin/view_earnings.html', context)















from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.db.models import Sum
from .models import ParkingSpace, Booking, Notification, User

# In your admin_dashboard view
from .models import ParkEasyUser

@user_passes_test(is_superuser)
def admin_dashboard(request):
    total_users = User.objects.count()
    total_parking_spaces = ParkingSpace.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(status='Completed').aggregate(total_revenue=Sum('price_paid'))['total_revenue'] or 0

    unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    # Get the ParkEasyUser object for the logged-in user
    parkeasy_user = ParkEasyUser.objects.get(user=request.user)
    user_role = parkeasy_user.get_role()  # Get the user's role

    context = {
        'total_users': total_users,
        'total_parking_spaces': total_parking_spaces,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'unread_notifications_count': unread_notifications_count,
        'user_role': user_role,  # Pass the role to the template
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
    return render(request, 'delete_booking_confirmation.html', {'booking': booking})  



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


from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import Notification
import logging

logger = logging.getLogger(__name__)  # Set up logging

# Modify the view to add notification creation
@user_passes_test(is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        # Delete the user
        user.delete()

        # Create a notification for the admin about the deletion
        notification_message = f"User '{user.username}' has been deleted by {request.user.username}."
        admin_user = User.objects.get(is_superuser=True)  # Assuming the admin is a superuser
        Notification.objects.create(
            user=admin_user,
            message=notification_message,
            notification_type='USER_DELETION'  # New notification type for user deletion
        )

        # Log the deletion
        logger.info(f"User '{user.username}' (ID: {user.id}) was deleted by admin {request.user.username}.")

        # Success message and redirect
        messages.success(request, f"User '{user.username}' deleted successfully.")
        return redirect('manage_users')

    return render(request, 'admin/confirm_delete_user.html', {'user': user})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.timezone import now
from .models import Payment, Booking, Notification
from django.contrib.auth.models import User

@login_required
def payment_form_view(request):
    booking_id = request.GET.get('booking_id')
    if not booking_id:
        return JsonResponse({'error': 'Booking ID is required.'}, status=400)

    try:
        booking = Booking.objects.get(id=booking_id, user=request.user.parkeasyuser)
        parking_host = booking.parking_space.host  # Assuming `parking_space` has a `host` field
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found or access denied.'}, status=404)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'card')  # Default to card
        try:
            # Create the payment
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.price_paid,  # Use price_paid field here
                payment_date=now(),
                payment_method=payment_method,
                payment_status='paid'  # Assuming successful for now
            )
            booking.status = 'confirmed'
            booking.save()

            # Notifications for the driver
            Notification.objects.create(
                user=request.user,
                message=f"Your payment of {payment.amount} has been successfully processed.",
                notification_type='PAYMENT_CONFIRM'
            )
            Notification.objects.create(
                user=request.user,
                message=f"Your booking at '{booking.parking_space.name}' has been successfully confirmed.",
                notification_type='BOOKING_CONFIRM'
            )

            # Notifications for the host
            Notification.objects.create(
                user=parking_host.user,  # Assuming the host is related to the User model
                message=f"A booking has been confirmed for your parking space at '{booking.parking_space.name}'.",
                notification_type='BOOKING_CONFIRM'
            )
            Notification.objects.create(
                user=parking_host.user,
                message=f"You have received a payment of {payment.amount} for a booking at '{booking.parking_space.name}'.",
                notification_type='PAYMENT_CONFIRM'
            )

            # Notifications for the admin (assuming admin users are superusers)
            admin_users = User.objects.filter(is_superuser=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    message=f"A payment of {payment.amount} has been processed for booking '{booking.parking_space.name}' by {request.user.username}.",
                    notification_type='ADMIN_PAYMENT'
                )

            return JsonResponse({
                'amount': payment.amount,
                'date_time': payment.payment_date.strftime('%B %d, %Y, %I:%M %p'),
                'reference_number': f'PAY-{payment.id}',
                'message': 'Payment Successful!'
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'payment/payment_form.html', {'booking': booking})










from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import ParkingSpace, Review
from .forms import ReviewForm
from .models import ParkEasyUser

# View for displaying all reviews for a particular parking space
def parking_space_reviews(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id)
    reviews = Review.objects.filter(parking_space=parking_space)
    user = get_object_or_404(ParkEasyUser, user=request.user)

    # Check if the user has already reviewed the parking space
    user_has_reviewed = Review.objects.filter(parking_space=parking_space, user=user).exists()

    if user_has_reviewed:
        messages.error(request, "You have already reviewed this parking space.")

    return render(request, 'parking/parking_space_reviews.html', {
        'parking_space': parking_space,
        'reviews': reviews,
        'user_has_reviewed': user_has_reviewed
    })


def add_review(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id)
    user = get_object_or_404(ParkEasyUser, user=request.user)

    # Check if the user has already reviewed the parking space
    if Review.objects.filter(parking_space=parking_space, user=user).exists():
        messages.error(request, "You have already reviewed this parking space.")
        return redirect('parking_space_reviews', space_id=space_id)

    # Handle the review submission
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.parking_space = parking_space
            review.user = user
            review.save()
            messages.success(request, "Review added successfully.")
            return redirect('parking_space_reviews', space_id=space_id)
    else:
        form = ReviewForm()

    return render(request, 'parking/add_review.html', {'parking_space': parking_space, 'form': form})


# View for editing a review
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import ParkingSpace, Review
from .forms import ReviewForm
from .models import ParkEasyUser

# View for editing an existing review
def edit_review(request, space_id, review_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id)
    review = get_object_or_404(Review, id=review_id)
    user = get_object_or_404(ParkEasyUser, user=request.user)

    # Check if the review belongs to the current user
    if review.user != user:
        messages.error(request, "You can only edit your own reviews.")
        return redirect('parking_space_reviews', space_id=space_id)

    # Handle the review editing
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully.")
            return redirect('parking_space_reviews', space_id=space_id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'parking/edit_review.html', {'parking_space': parking_space, 'form': form, 'review': review})


from django.shortcuts import get_object_or_404, redirect
from .models import Review
from django.contrib import messages

def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Check if the logged-in user is the one who wrote the review
    if review.user.user == request.user:
        review.delete()
        messages.success(request, "Review deleted successfully.")
    else:
        messages.error(request, "You can only delete your own reviews.")

    # Redirect back to the parking space reviews page
    return redirect('parking_space_reviews', space_id=review.parking_space.id)


@login_required
def notifications_view(request):
    # Get all notifications for the logged-in user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/notifications_page.html', {'notifications': notifications})

from django.shortcuts import get_object_or_404, redirect
from .models import Notification

@login_required
def mark_notification_as_read(request, notification_id):
    # Get the specific notification and mark it as read
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications_page')


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages  # Import messages
from .models import Notification

@login_required
def delete_notification(request, notification_id):
    # Get the specific notification to delete
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    # Delete the notification
    notification.delete()

    # Add success message for the delete action
    messages.success(request, 'Notification deleted successfully.')

    # Redirect to the notifications page
    return redirect('notifications_page')


