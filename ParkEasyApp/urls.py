from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page route
    path('dashboard/', views.dashboard, name='dashboard'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register_view, name='register'),
    # Add more URLs as needed
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('about/', views.about, name='about'),  # Ensure 'about' view is correctly defined here
    path('help-support/', views.help_support, name='help_support'),
    path('faq/', views.faq, name='faq'),
    path('terms_conditions/', views.terms_conditions, name='terms_conditions'),
    # Parking Space URLs
    path('parking-spaces/', views.parking_space_list_view, name='parking_space_list'),
    path('parking-spaces/<int:space_id>/', views.parking_space_detail_view, name='parking_space_detail'),
    path('parking-spaces/add/', views.add_parking_space_view, name='add_parking_space'),
    path('parking-spaces/edit/<int:space_id>/', views.edit_parking_space_view, name='edit_parking_space'),
    path('parking-spaces/delete/<int:space_id>/', views.delete_parking_space_view, name='delete_parking_space'),
    path('listed-parking-spaces/', views.my_listed_parking_spaces, name='my_listed_parking_spaces')


]

