from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import *  # If you have any models to import

# Home view
def Home(request):
    return render(request, 'ParkEasy/index.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        # Get username and password from the form
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Log the user in
            login(request, user)
            return redirect('home')  # Redirect to the homepage after successful login
        else:
            # If authentication fails, show an error message
            return render(request, 'ParkEasy/login.html', {'error': 'Invalid credentials'})

    return render(request, 'ParkEasy/login.html')

