from django.contrib import admin

# Register your models here.
from .models import Service, ServiceCategory, Master, Client, Appointment, Review, Admin

# Register your models here.

admin.site.register(Service)
admin.site.register(ServiceCategory)
admin.site.register(Master)
admin.site.register(Client)
admin.site.register(Appointment)
admin.site.register(Review)
admin.site.register(Admin)
