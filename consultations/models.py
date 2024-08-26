from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_specialist = models.BooleanField(default=False)
    is_client = models.BooleanField(default=True)


class Specialist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class Slot(models.Model):
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    service_type = models.CharField(max_length=100)


class Consultation(models.Model):
    slot = models.OneToOneField(Slot, on_delete=models.CASCADE)
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    cancellation_reason = models.CharField(max_length=255, blank=True, null=True)
