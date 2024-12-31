from django.db import models
from django.contrib.auth.models import User  # Using Django's built-in User model for authentication

# User Model (extending the default Django User model)
class ParkEasyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Linking to Django's built-in User model
    role = models.CharField(
        max_length=50,
        choices=[('driver', 'Driver'), ('host', 'Host'), ('both', 'Both')],
        default='driver'
    )

    def __str__(self):
        return self.user.username


# Parking Space Model (for Hosts to list their parking spaces)
class ParkingSpace(models.Model):
    host = models.ForeignKey(ParkEasyUser, on_delete=models.CASCADE, related_name="parking_spaces")
    location = models.CharField(max_length=255)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    availability = models.BooleanField(default=True)  # If space is available for reservation
    amenities = models.TextField(blank=True, null=True)  # Optional amenities description
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # Average rating by drivers
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the parking space was added

    def __str__(self):
        return f"Parking Space {self.id} by {self.host.user.username}"

    class Meta:
        indexes = [
            models.Index(fields=['host', 'location']),
        ]


# Booking Model (for Drivers to book parking spaces)
class Booking(models.Model):
    driver = models.ForeignKey(ParkEasyUser, on_delete=models.CASCADE, related_name="bookings")
    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    booking_time = models.DateTimeField()
    start_time = models.DateTimeField()  # Explicit start time for the booking
    end_time = models.DateTimeField()  # Explicit end time for the booking
    duration = models.DurationField()  # Duration of the booking
    price_paid = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[('booked', 'Booked'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        default='booked'
    )
    time_extension = models.DurationField(null=True, blank=True)  # If driver requests more time
    grace_period = models.DurationField(null=True, blank=True)  # Grace period for short delays

    def __str__(self):
        return f"Booking by {self.driver.user.username} for space {self.parking_space.id}"

    class Meta:
        indexes = [
            models.Index(fields=['driver', 'parking_space', 'status']),
        ]


# Payment Model (for managing payments for bookings)
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[('stripe', 'Stripe'), ('paypal', 'PayPal')])
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
        default='pending'
    )

    def __str__(self):
        return f"Payment of {self.amount} for booking {self.booking.id}"

    class Meta:
        indexes = [
            models.Index(fields=['booking', 'payment_status']),
        ]


# Reviews Model (for drivers to rate parking spaces after use)
class Review(models.Model):
    driver = models.ForeignKey(ParkEasyUser, on_delete=models.CASCADE)
    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=2, choices=[(i/10, str(i/10)) for i in range(1, 51)])  # Allow fractional ratings
    comment = models.TextField(blank=True, null=True)  # Optional review comment
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.driver.user.username} for space {self.parking_space.id}"

    class Meta:
        unique_together = ('driver', 'parking_space')  # Ensure a driver can only review a space once
        indexes = [
            models.Index(fields=['driver', 'parking_space']),
        ]


# Notifications Model (for managing notifications for both drivers and hosts)
class Notification(models.Model):
    user = models.ForeignKey(ParkEasyUser, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=[('booking', 'Booking'), ('payment', 'Payment'), ('reminder', 'Reminder')])
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.user.username}: {self.message[:30]}..."

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]


# Optional Model for Time Extension Requests (to handle driver time extension requests)
class TimeExtensionRequest(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    requested_extension = models.DurationField()
    approved = models.BooleanField(default=False)
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Extension request for booking {self.booking.id}"

    class Meta:
        indexes = [
            models.Index(fields=['booking', 'approved']),
        ]


# Grace Period Model (for hosts to set grace periods for short-term bookings)
class GracePeriod(models.Model):
    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    grace_period_duration = models.DurationField()  # Grace period duration (e.g., 15 minutes)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Grace period for space {self.parking_space.id}: {self.grace_period_duration}"

    class Meta:
        indexes = [
            models.Index(fields=['parking_space']),
        ]


# Earnings Tracking for Parking Hosts
class Earnings(models.Model):
    host = models.ForeignKey(ParkEasyUser, on_delete=models.CASCADE)
    amount_earned = models.DecimalField(max_digits=10, decimal_places=2)
    date_earned = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[('stripe', 'Stripe'), ('paypal', 'PayPal')])

    def __str__(self):
        return f"Earnings of {self.amount_earned} for host {self.host.user.username} on {self.date_earned.date()}"

    class Meta:
        indexes = [
            models.Index(fields=['host', 'date_earned']),
        ]

