from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import ParkEasyUser
from .forms import CustomUserCreationForm  # Add this line to import the form


# Login View
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after login
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')



# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout


from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import ParkEasyUser

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user to the database
            
            # Create the ParkEasyUser instance with default role 'driver'
            ParkEasyUser.objects.create(user=user, role='driver')  # Set a default role, 'driver', for the user
            
            # Show success message
            messages.success(request, 'Your account has been created successfully! You can now log in.')
            
            # Redirect to login page
            return redirect('login')  # Make sure the 'login' URL name exists in your urls.py
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})







from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import ParkEasyUser

# Profile View
@login_required
def profile_view(request):
    if request.method == "POST":
        user = request.user

        # Update the user's email
        if 'email' in request.POST:
            user.email = request.POST['email']
            user.save()

        # Update the role (optional)
        try:
            park_easy_user = ParkEasyUser.objects.get(user=user)
            if 'role' in request.POST and request.POST['role'] in ['driver', 'host', 'both']:
                park_easy_user.role = request.POST['role']
                park_easy_user.save()
        except ParkEasyUser.DoesNotExist:
            messages.error(request, "User profile not found. Please contact support.")
            return redirect('home')  # Or a relevant fallback page

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')  # Redirect to the profile page after updating

    return render(request, 'profile.html')


from django.shortcuts import render
from django.db.models import Q
from .models import ParkingSpace

def parking_space_list_view(request):
    query = request.GET.get('q', '')  # Search query (e.g., location)
    parking_spaces = ParkingSpace.objects.filter(
        Q(location__icontains=query) & Q(availability=True)  # Available spaces
    ).order_by('-created_at')  # Newest first

    return render(request, 'parking_space_list.html', {
        'parking_spaces': parking_spaces,
        'query': query
    })

from django.shortcuts import get_object_or_404

def parking_space_detail_view(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id)

    return render(request, 'parking_space_detail.html', {
        'parking_space': parking_space
    })


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import ParkingSpaceForm  # Assume a form for ParkingSpace exists

@login_required
def add_parking_space_view(request):
    if request.method == 'POST':
        form = ParkingSpaceForm(request.POST)
        if form.is_valid():
            parking_space = form.save(commit=False)
            parking_space.host = request.user.parkeasyuser  # Assign the current user as the host
            parking_space.save()
            return HttpResponseRedirect(reverse('parking_space_list'))
    else:
        form = ParkingSpaceForm()

    return render(request, 'add_parking_space.html', {
        'form': form
    })


@login_required
def edit_parking_space_view(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id, host=request.user.parkeasyuser)

    if request.method == 'POST':
        form = ParkingSpaceForm(request.POST, instance=parking_space)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('parking_space_detail', args=[space_id]))
    else:
        form = ParkingSpaceForm(instance=parking_space)

    return render(request, 'edit_parking_space.html', {
        'form': form,
        'parking_space': parking_space
    })


from django.http import HttpResponseRedirect

@login_required
def delete_parking_space_view(request, space_id):
    parking_space = get_object_or_404(ParkingSpace, id=space_id, host=request.user.parkeasyuser)

    if request.method == 'POST':
        parking_space.delete()
        return HttpResponseRedirect(reverse('parking_space_list'))

    return render(request, 'delete_parking_space.html', {
        'parking_space': parking_space
    })


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
@login_required
def dashboard(request):
    user = request.user

    # Try to get the ParkEasyUser instance
    try:
        parkeasy_user = ParkEasyUser.objects.get(user=user)
    except ParkEasyUser.DoesNotExist:
        # Create ParkEasyUser instance if not found
        parkeasy_user = ParkEasyUser.objects.create(user=user, role='driver')  # Default role, can be updated later
        messages.success(request, "Your profile has been created. You can now add parking spaces.")

    parking_spaces = ParkingSpace.objects.filter(host=parkeasy_user)

    # Render the dashboard with the parking spaces
    return render(request, 'parkeasy/dashboard.html', {'parking_spaces': parking_spaces})



# views.py

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # Render the home page


from django.shortcuts import render

def about(request):
    return render(request, 'parkeasy/about.html')


def contact(request):
    return render(request, 'contact.html')  # Render the contact page




