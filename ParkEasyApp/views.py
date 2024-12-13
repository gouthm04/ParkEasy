from django.shortcuts import render
from. models import*

# Create your views here.

def Home(request):
    data=DriverRegistration.objects.all()
    return render(request,'ParkEasy/index.html',context={"Data":data})
    
