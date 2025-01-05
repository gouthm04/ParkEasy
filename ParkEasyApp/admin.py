from django.contrib import admin
from .models import ParkEasyUser, ParkingSpace, Booking, Payment, Review, Notification, TimeExtensionRequest, GracePeriod, Earnings

class ParkEasyUserAdmin(admin.ModelAdmin):
    # Adjusted list_display to use user fields and role if needed
    list_display = ('user', 'get_role')  # Using a method 'get_role' instead of a non-existent 'role' field
    search_fields = ['user__username', 'user__email']

    def get_role(self, obj):
        return obj.user.groups.first().name if obj.user.groups.exists() else 'No role assigned'
    get_role.short_description = 'Role'

# Registering ParkEasyUser with custom admin
admin.site.register(ParkEasyUser, ParkEasyUserAdmin)

class ParkingSpaceAdmin(admin.ModelAdmin):
    list_display = ('location', 'price_per_hour', 'availability', 'rating', 'host')  
    search_fields = ['location']
    list_filter = ('availability',)  # Added filter for availability

class BookingAdmin(admin.ModelAdmin):
    # Changed 'driver' to 'user' which is the correct field
    list_display = ('user', 'parking_space', 'booking_time', 'status', 'price_paid')
    list_filter = ('status', 'start_date', 'end_date')  # Added filters for date ranges

# Registering models with custom admin views
admin.site.register(ParkingSpace, ParkingSpaceAdmin)
admin.site.register(Booking, BookingAdmin)

# Registering other models without custom admin views
admin.site.register(Payment)
admin.site.register(Review)
admin.site.register(Notification)
admin.site.register(TimeExtensionRequest)
admin.site.register(GracePeriod)
admin.site.register(Earnings)
