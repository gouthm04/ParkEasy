from django.urls import path
from. import views


urlpatterns = [
    path('Homepage/',views.Home, name='home'),
    path('login/',views.login, name='login')
    
]