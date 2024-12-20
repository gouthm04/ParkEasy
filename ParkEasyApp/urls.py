from django.urls import path
from. import views


urlpatterns = [
    path('Homepage/',views.Home, name='home'),
    path('login/',views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),  # Add logout path
    
]