from datetime import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User  # Using Django's built-in User model for authentication
from django.db.models.signals import post_save
from django.dispatch import receiver


class ParkEasyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('suspended', 'Suspended'), ('pending', 'Pending')], default='active')

    def __str__(self):
        return self.user.username

    def get_role(self):
        if self.user.is_superuser:
            return 'admin'
        # If the user has both parking spaces listed (host) and bookings (driver), return 'both'
        elif self.parking_spaces.exists() and self.bookings.exists():
            return 'both'
        elif self.parking_spaces.exists():
            return 'host'
        elif self.bookings.exists():
            return 'driver'
        return 'user'  # If none of the above, treat as a regular user


# Parking Space Model (for listing parking spaces)
from django.db import models

class ParkingSpace(models.Model):
    name = models.CharField(max_length=255)
    host = models.ForeignKey(ParkEasyUser, on_delete=models.CASCADE, related_name="parking_spaces")
    location = models.CharField(max_length=255)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)
    amenities = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to="parking_images/", null=True, blank=True)  # Image field

    def __str__(self):
        return f"Parking Space {self.id} at {self.location}"

    class Meta:
        indexes = [
            models.Index(fields=['host', 'location']),
        ]



from django.db import models
from django.utils import timezone
from datetime import datetime
from decimal import Decimal

class Booking(models.Model):
    user = models.ForeignKey(ParkEasyUser, on_delete=models.CASCADE, related_name="bookings")
    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)  # Auto-set to the time of booking
    start_date = models.DateField(default=timezone.now)  # Dynamically use current date
    start_time = models.TimeField()
    end_date = models.DateField(default=timezone.now)  # Dynamically use current date
    end_time = models.TimeField()
    duration = models.DurationField()
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('booked', 'Booked'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        default='booked'
    )
    time_extension = models.DurationField(null=True, blank=True)  # Optional additional booking time
    grace_period = models.DurationField(null=True, blank=True)  # Grace period for delays

    def save(self, *args, **kwargs):
        # Calculate the duration before saving
        if self.start_date and self.start_time and self.end_date and self.end_time:
            start_datetime = datetime.combine(self.start_date, self.start_time)
            end_datetime = datetime.combine(self.end_date, self.end_time)

            # Set the duration based on the difference between start and end times
            self.duration = end_datetime - start_datetime
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.user.user.username} at {self.parking_space.location}"

    class Meta:
        indexes = [
            models.Index(fields=['user', 'parking_space', 'status']),
        ]
        unique_together = ('parking_space', 'start_time', 'end_time'),



# PAYMENT MODEL
from django.db import models
from django.utils.timezone import now

class Payment(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    payment_date = models.DateTimeField(default=now)  # Use default for manual date handling
    
    payment_method = models.CharField(
        max_length=50,
        choices=[('stripe', 'Stripe'), ('paypal', 'PayPal'), ('card', 'Credit/Debit Card')],
        default='card'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
        default='pending'
    )

    def __str__(self):
        return f"Payment of ₹{self.amount} for Booking ID {self.booking.id}"

    class Meta:
        indexes = [
            models.Index(fields=['booking', 'payment_status']),
        ]


# Review Model
class Review(models.Model):
    user = models.ForeignKey(ParkEasyUser, on_delete=models.CASCADE , null=True ,blank=True)
    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE , null=True ,blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    comment = models.TextField(blank=True, null=True)  # Optional review comment
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.user.username} for {self.parking_space.name}"

    

# Notifications Model
from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('BOOKING_CONFIRM', 'Booking Confirmation'),
        ('PAYMENT_CONFIRM', 'Payment Confirmation'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('PARKING_AVAILABLE', 'Parking Available'),
        ('EXTENSION_REQUEST', 'Time Extension Request'),
        ('GRACE_PERIOD', 'Grace Period Expiry'),
        ('USER_REGISTRATION', 'New User Registration'),  # Added this line
        ('ADMIN_PAYMENT', 'Admin Payment Notification'),
        ('NEW_PARKING_SPACE', 'New Parking Space Created'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # user to whom the notification belongs
    message = models.CharField(max_length=500)  # the notification message
    notification_type = models.CharField(choices=NOTIFICATION_TYPES, max_length=50)
    is_read = models.BooleanField(default=False)  # Add this line for the 'is_read' field
    created_at = models.DateTimeField(auto_now_add=True)  # timestamp when the notification is created

    def __str__(self):
        return f"Notification for {self.user.username} - {self.notification_type}"






# Time Extension Request Model
class TimeExtensionRequest(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    requested_extension = models.DurationField()
    approved = models.BooleanField(default=False)
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Time extension request for booking {self.booking.id}"

    class Meta:
        indexes = [
            models.Index(fields=['booking', 'approved']),
        ]


# Grace Period Model
class GracePeriod(models.Model):
    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    grace_period_duration = models.DurationField()  # E.g., 15 minutes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Grace period for {self.parking_space.location}: {self.grace_period_duration}"

    class Meta:
        indexes = [
            models.Index(fields=['parking_space']),
        ]


# Earnings Model
class Earnings(models.Model):
    host = models.ForeignKey(ParkEasyUser, on_delete=models.CASCADE)
    amount_earned = models.DecimalField(max_digits=10, decimal_places=2)
    date_earned = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[('stripe', 'Stripe'), ('paypal', 'PayPal')])

    def __str__(self):
        return f"Earnings of ₹{self.amount_earned} for {self.host.user.username} on {self.date_earned.date()}"

    class Meta:
        indexes = [
            models.Index(fields=['host', 'date_earned']),
        ]
