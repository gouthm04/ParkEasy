from django.shortcuts import render
from. models import*

# Create your views here.

def Home(request):
    
    return render(request,'ParkEasy/index.html')

def login(request):
    return render(request,'ParkEasy/login.html')
    
    
