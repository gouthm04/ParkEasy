from django.contrib import admin
from .models import ParkEasyUser, ParkingSpace, Booking, Payment, Review, Notification, TimeExtensionRequest, GracePeriod, Earnings

class ParkEasyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')  # Display these fields in the admin list
    search_fields = ['user__username', 'user__email']  # Add a search bar for username and email

# Registering only once with the custom admin
admin.site.register(ParkEasyUser, ParkEasyUserAdmin)

class ParkingSpaceAdmin(admin.ModelAdmin):
    list_display = ('location', 'price_per_hour', 'availability', 'rating', 'host')  # Show these fields in the list
    search_fields = ['location']  # Add a search bar for location

class BookingAdmin(admin.ModelAdmin):
    list_display = ('driver', 'parking_space', 'booking_time', 'status', 'price_paid')
    list_filter = ('status',)  # Add a filter for booking status

admin.site.register(ParkingSpace, ParkingSpaceAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Payment)
admin.site.register(Review)
admin.site.register(Notification)
admin.site.register(TimeExtensionRequest)
admin.site.register(GracePeriod)
admin.site.register(Earnings)
