from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone



# Модель для "Категорії послуг"
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    photo = models.FileField(upload_to="photos/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Модель для "Види послуг"
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField()  # Тривалість в хвилинах
    photo = models.FileField(upload_to="photos/", blank=True, null=True)

    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Admin(models.Model):
    full_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255)
    photo = models.FileField(upload_to="photos/", blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    instagram = models.CharField(max_length=255, blank=True, null=True)
    twitter = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name


class Master(models.Model):
    full_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255)
    photo = models.FileField(upload_to="photos/", blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    instagram = models.CharField(max_length=255, blank=True, null=True)
    twitter = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"id:{self.pk} {self.full_name}"


class Client(models.Model):
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    photo = models.FileField(upload_to="photos/", blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"id:{self.pk} {self.full_name}"


class Appointment(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now) 
    start_time = models.TimeField()

    def calculate_end_time(self):
        # Calculate end_time by adding the duration of the service to the start_time
        return (
            datetime.combine(self.date, self.start_time)
            + timedelta(minutes=self.service.duration)
        ).time()

    end_time = property(calculate_end_time)

    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"id:{self.pk}"


class Review(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    text = models.TextField()

    is_confirmed = models.BooleanField(default=False)

