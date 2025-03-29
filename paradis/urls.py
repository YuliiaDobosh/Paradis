from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("appointments", views.appointments, name="appointments"),
    path("masters", views.masters, name="masters"),
    path("services", views.services, name="services"),
    path("profile", views.profile, name="profile"),
    path("error", views.error, name="error"),
    path("review", views.review, name="review"),
    path("confirm/<str:object_type>/<int:object_id>/", views.confirm, name="confirm"),
    path("delete/<str:object_type>/<int:object_id>/", views.delete, name="delete"),
    path("edit/<str:object_type>/<int:object_id>/", views.edit, name="edit"),
    path('service-picker/', views.service_picker, name='service_picker'),
    path('chat/', views.chatbot_picker, name='chatbot_picker'),
]
