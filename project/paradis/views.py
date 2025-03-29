from django.shortcuts import render, redirect, get_object_or_404
from .models import Service, ServiceCategory, Master, Client, Appointment, Admin, Review
from django.contrib.auth.decorators import login_required
from django import template
from django.template.defaultfilters import time
from datetime import datetime

register = template.Library()

def index(request):
    """
    Displays the main page with services, service categories, masters, and reviews.
    """
    user = request.user
    is_client, is_master, is_admin = user_type(request)

    services = Service.objects.all()
    service_categories = ServiceCategory.objects.all()
    masters = Master.objects.all()
    reviews = Review.objects.filter(is_confirmed=True)

    context = {
        "services": services,
        "service_categories": service_categories,
        "masters": masters,
        "is_client": is_client,
        "is_master": is_master,
        "is_admin": is_admin,
        "reviews": reviews
    }
    return render(request, "public/index.html", context)

@login_required
def appointments(request):
    """
    Handles the logic for displaying and managing appointments for clients, masters, and admin.
    """
    user = request.user
    is_client, is_master, is_admin = user_type(request)

    if is_client:
        _user = Client.objects.get(user=user)
        appointments = Appointment.objects.filter(client=_user)
    elif is_master:
        _user = Master.objects.get(user=user)
        appointments = Appointment.objects.filter(master=_user)
    else:
        _user = Admin.objects.get(user=user)
        appointments = Appointment.objects.all()

    # Handling appointment creation
    if request.method == "POST":
        service_id = request.POST["service"]
        master_id = request.POST["master"]
        client_id = request.POST["client"]
        date = request.POST["date"]
        start_time = request.POST["start_time"]

        master = Master.objects.get(pk=master_id)
        client = Client.objects.get(pk=client_id)

        appointment = Appointment.objects.create(
            service_id=service_id,
            client=client,
            master=master,
            date=date,
            start_time=start_time,
        )
        appointment.save()
        return redirect("appointments")

    # Handling appointment filtering
    filter_params = {}
    service_id = request.GET.get("service")
    master_id = request.GET.get("master")
    client_id = request.GET.get("client")
    date = request.GET.get("date")
    start_time = request.GET.get("start_time")

    if service_id:
        filter_params["service"] = get_object_or_404(Service, pk=service_id)

    if master_id:
        filter_params["master"] = get_object_or_404(Master, pk=master_id, is_confirmed=True)

    if client_id:
        filter_params["client"] = get_object_or_404(Client, pk=client_id)

    if date:
        filter_params["date"] = date
    else:
        filter_params["date"] = datetime.now().date()

    if start_time:
        filter_params["start_time"] = start_time

    if filter_params:
        appointments = appointments.filter(**filter_params)

    # Calculating total profit from appointments
    profit = sum([a.service.price for a in appointments])

    masters = Master.objects.filter(is_confirmed=True)
    clients = Client.objects.all()
    services = Service.objects.all()

    context = {
        "is_client": is_client,
        "is_master": is_master,
        "is_admin": is_admin,
        "s_user": _user,
        "appointments": appointments,
        "masters": masters,
        "clients": clients,
        "services": services,
        "profit": profit,
    }
    return render(request, "public/appointments.html", context)

def services(request):
    """
    Handles the logic for displaying and managing services.
    """
    user = request.user
    is_client, is_master, is_admin = user_type(request)

    # Handling service creation
    if request.method == "POST":
        name = request.POST["name"]
        category_id = request.POST["service_category"]
        description = request.POST["description"]
        price = request.POST["price"]
        duration = request.POST["duration"]

        category = ServiceCategory.objects.get(pk=category_id)

        service = Service.objects.create(
            name=name,
            category=category,
            description=description,
            price=price,
            duration=duration,
        )
        if "photo" in request.FILES:
            service.photo = request.FILES["photo"]
        service.save()
        return redirect("services")

    services = Service.objects.all()
    service_categories = ServiceCategory.objects.all()

    context = {
        "is_client": is_client,
        "is_master": is_master,
        "is_admin": is_admin,
        "services": services,
        "service_categories": service_categories,
    }
    return render(request, "public/services.html", context)

@login_required
def masters(request):
    """
    Handles the logic for displaying and managing masters for admin.
    """
    user = request.user
    is_client, is_master, is_admin = user_type(request)

    if is_admin:
        _user = Admin.objects.get(user=user)
        masters = Master.objects.all()
    else:
        return error(request, "You must be an admin")

    filter_params = {}

    master_id = request.GET.get("master_id")
    phone_number = request.GET.get("client")
    email = request.GET.get("email")

    if master_id:
        filter_params["pk"] = master_id

    if phone_number:
        filter_params["phone_number"] = phone_number

    if email:
        filter_params["email"] = email

    if filter_params:
        masters = masters.filter(**filter_params)

    context = {
        "is_client": is_client,
        "is_master": is_master,
        "is_admin": is_admin,
        "s_user": _user,
        "masters": masters,
    }
    return render(request, "public/masters.html", context)

@login_required
def profile(request):
    """
    Displays the profile page for clients, masters, and admin.
    """
    user = request.user
    is_client, is_master, is_admin = user_type(request)

    if is_client:
        _user = Client.objects.get(user=user)
        appointments = Appointment.objects.filter(client=_user)
    elif is_master:
        _user = Master.objects.get(user=user)
        appointments = Appointment.objects.filter(master=_user)
    elif is_admin:
        _user = Admin.objects.get(user=user)
        appointments = Appointment.objects.all()

    masters = Master.objects.all()
    reviews = Review.objects.all()

    context = {
        "s_user": _user,
        "is_client": is_client,
        "is_master": is_master,
        "is_admin": is_admin,
        "appointments": appointments,
        "masters": masters,
        "reviews": reviews
    }
    return render(request, "public/profile.html", context)


def user_type(request):
    """
    Determines the type of user (client, master, admin) based on authentication status.
    """
    user = request.user
    is_client = False
    is_master = False
    is_admin = False

    if user.is_authenticated:
        try:
            _user = Client.objects.get(user=user)
            is_client = True
        except Client.DoesNotExist:
            try:
                _user = Master.objects.get(user=user)
                is_master = True
            except Master.DoesNotExist:
                try:
                    _user = Admin.objects.get(user=user)
                    is_admin = True
                except Admin.DoesNotExist:
                    return error(request, "User does not exist")
    return is_client, is_master, is_admin

def error(request, *args):
    """
    Displays an error page with the given error messages.
    """
    context = {
        "errors": args,
    }
    return render(request, "public/404.html", context)

def confirm(request, object_type, object_id):
    """
    Handles confirmation of various objects such as masters, appointments, services, and reviews.
    """
    if object_type == "master":
        obj = get_object_or_404(Master, pk=object_id)
        obj.is_confirmed = True
        obj.save()
        return redirect("masters")
    elif object_type == "appointment":
        obj = get_object_or_404(Appointment, pk=object_id)
        obj.is_confirmed = True
        obj.save()
        return redirect("appointments")
    elif object_type == "service":
        obj = get_object_or_404(Service, pk=object_id)
        obj.is_confirmed = True
        obj.save()
        return redirect("services")
    elif object_type == "review":
        obj = get_object_or_404(Review, pk=object_id)
        obj.is_confirmed = True
        obj.save()
        return redirect("profile")
    else:
        # Handle invalid object_type
        return error(request, "Invalid object_type")

def delete(request, object_type, object_id):
    """
    Handles deletion of various objects such as masters, appointments, clients, service categories, and reviews.
    """
    if object_type == "master":
        obj = get_object_or_404(Master, pk=object_id)
        obj.is_confirmed = True
        return redirect("masters")
    elif object_type == "appointment":
        obj = get_object_or_404(Appointment, pk=object_id)
        obj.delete()
        return redirect("appointments")
    elif object_type == "client":
        obj = get_object_or_404(Appointment, pk=object_id)
        obj.delete()
        return redirect("clients")
    elif object_type == "service_category":
        obj = get_object_or_404(ServiceCategory, pk=object_id)
        obj.delete()
        return redirect("service_categories")
    elif object_type == "review":
        obj = get_object_or_404(Review, pk=object_id)
        obj.delete()
        return redirect("profile")
    else:
        # Handle invalid object_type
        return error(request, "Invalid object_type")

def edit(request, object_type, object_id):
    """
    Handles editing of various objects such as masters, admins, clients, appointments, services.
    """
    is_client, is_master, is_admin = user_type(request)

    masters = Master.objects.filter(is_confirmed=True)
    service_categories = ServiceCategory.objects.all()

    context = {
        "obj_type": object_type,
        "obj_id": object_id,
        "service_categories": service_categories,
        "masters": masters,
        "is_client": is_client,
        "is_master": is_master,
        "is_admin": is_admin,
    }

    if object_type == "master":
        obj = get_object_or_404(Master, pk=object_id)
        context["obj"] = obj
        if request.method == "POST":
            obj.full_name = request.POST["full_name"]
            obj.bio = request.POST["bio"]
            obj.address = request.POST["address"]
            obj.phone_number = request.POST["phone_number"]
            obj.instagram = request.POST["instagram"]
            obj.twitter = request.POST["twitter"]
            obj.facebook = request.POST["facebook"]
            if "photo" in request.FILES:
                obj.photo = request.FILES["photo"]
            obj.save()
            return redirect(profile)
        return render(request, "public/edit_master.html", context)

    # Similar handling for other object types...

    else:
        return error(request, "Invalid object_type")

def review(request):
    """
    Handles the creation of reviews.
    """
    if request.method == "POST":
        text = request.POST["text"]
        client_id = request.POST["client_id"]
        client = get_object_or_404(Client, pk=client_id)
        review = Review.objects.create(client=client, text=text)
        review.save()
        return redirect(profile)