from django.db import models

# Create your models here.

class GenderChoices(models.TextChoices):
    MALE="Male","Male"
    FEMALE="Female","Female"
    OTHER="Other","Other"

class DriverRegistration (models.Model) :
    phone=models.CharField(max_length=10)
    gender=models.TextField(max_length=10,choices=GenderChoices.choices, null=True,blank=True)
    address=models.TextField(null=True,blank=True)
    vehicle=models.CharField(max_length=30)
    vehicle_no=models.CharField(max_length=10)


    def __str__(self):
        return f'driver {self.phone}'