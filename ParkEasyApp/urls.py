from django.urls import path
from . import views

urlpatterns = [
    # General Routes
    path('', views.home, name='home'),  
    path('dashboard/', views.dashboard, name='dashboard'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('about/', views.about, name='about'),
    path('help-support/', views.help_support, name='help_support'),
    path('faq/', views.faq, name='faq'),
    path('terms_conditions/', views.terms_conditions, name='terms_conditions'),

    # Parking Space Routes
    path('parking-spaces/', views.parking_space_list_view, name='parking_space_list'),
    path('parking-spaces/<int:space_id>/', views.parking_space_detail_view, name='parking_space_detail'),
    path('parking-spaces/add/', views.add_parking_space_view, name='add_parking_space'),
    path('parking-spaces/edit/<int:space_id>/', views.edit_parking_space_view, name='edit_parking_space'),
    path('parking-spaces/delete/<int:space_id>/', views.delete_parking_space_view, name='delete_parking_space'),
    path('listed-parking-spaces/', views.my_listed_parking_spaces, name='my_listed_parking_spaces'),
    path('add_review/<int:space_id>/', views.add_review, name='add_review'),
    path('parking_space/<int:space_id>/reviews/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('parking_space/<int:space_id>/reviews/', views.parking_space_reviews, name='parking_space_reviews'),
    path('parking_space/reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),

    # Booking Routes
    path('create-booking/<int:parking_space_id>/', views.create_booking_view, name='create_booking'),
    path('booking/<int:booking_id>/', views.booking_detail_view, name='booking_detail'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('booking-success/', views.booking_success_view, name='booking_success'),

    # Payment Routes
    path('payment/', views.payment_form_view, name='payment_form'),

    # Earnings Routes
    path('view_earnings/', views.earnings_view, name='view_earnings'),

    # Map Route
    path('map/<int:space_id>/', views.map, name='map'),

    # Admin Routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('manage-parking-spaces/', views.manage_parking_spaces, name='manage_parking_spaces'),  
    path('manage-bookings/', views.manage_bookings, name='manage_bookings'),
    path('admin/edit-booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('admin/delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'), 
    path('reports/', views.reports, name='reports'),

    # Success URL for Parking Spaces
    path('parking-spaces/success/', views.success_view, name='success_url'),
    
]
