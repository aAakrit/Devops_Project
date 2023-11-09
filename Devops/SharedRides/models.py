from django.db import models
from django.contrib.auth.models import User


class Trip(models.Model):
    departure_location = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.CharField(max_length=100)
    available_seats = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.departure_location} to {self.destination}"


class Message(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
