# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from .models import Service, ServiceCategory, Master, Client, Appointment, Admin, Review
from django.contrib.auth.decorators import login_required
from django import template
from django.template.defaultfilters import time
from datetime import datetime
from .forms import ServiceFilterForm
from transformers import pipeline
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

register = template.Library()
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def index(request):
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

    filter_params = {}

    service_id = request.GET.get("service")
    master_id = request.GET.get("master")
    client_id = request.GET.get("client")
    date = request.GET.get("date")
    start_time = request.GET.get("start_time")

    if service_id:
        filter_params["service"] = get_object_or_404(Service, pk=service_id)

    if master_id:
        filter_params["master"] = get_object_or_404(
            Master, pk=master_id, is_confirmed=True
        )

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
    user = request.user

    is_client, is_master, is_admin = user_type(request)

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
        # "appointments": appointments,
        "masters": masters,
    }

    return render(request, "public/masters.html", context)


@login_required
def profile(request):
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
    context = {
        "errors": args,
    }
    return render(request, "public/404.html", context)


def confirm(request, object_type, object_id):
    if object_type == "master":
         obj = get_object_or_404(Master, pk=object_id)
         obj.delete()
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
    if object_type == "master":
        obj = get_object_or_404(Master, pk=object_id)
        obj.is_confirmed = True
        return redirect("masters")
    elif object_type == "appointment":
        obj = get_object_or_404(Appointment, pk=object_id)
        obj.delete()
        return redirect("appointments")
    elif object_type == "client":
        obj = get_object_or_404(Client, pk=object_id)
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

    elif object_type == "admin":
        obj = get_object_or_404(Admin, pk=object_id)
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
        return render(request, "public/edit_admin.html", context)

    elif object_type == "client":
        obj = get_object_or_404(Client, pk=object_id)
        context["obj"] = obj
        if request.method == "POST":
            obj.full_name = request.POST["full_name"]
            obj.address = request.POST["address"]
            obj.phone_number = request.POST["phone_number"]
            if "photo" in request.FILES:
                obj.photo = request.FILES["photo"]
            obj.save()
            return redirect(profile)
        return render(request, "public/edit_client.html", context)

    elif object_type == "appointment":
        obj = get_object_or_404(Appointment, pk=object_id)
        context["obj"] = obj
        if request.method == "POST":
            obj.date = request.POST["date"]
            obj.start_time = request.POST["start_time"]
            master_id = request.POST["master"]
            obj.master = get_object_or_404(Master, pk=master_id)
            obj.is_confirmed = False
            obj.save()
            return redirect(appointments)
        return render(request, "public/edit_appointment.html", context)

    elif object_type == "service":
        obj = get_object_or_404(Service, pk=object_id)
        context["obj"] = obj
        if request.method == "POST":
            obj.name = request.POST["name"]
            obj.price = request.POST["price"]
            obj.duration = request.POST["duration"]
            obj.description = request.POST["description"]
            obj.category = get_object_or_404(
                ServiceCategory, pk=request.POST["service_category"]
            )
            if "photo" in request.FILES:
                obj.photo = request.FILES["photo"]
            obj.save()
            return redirect(services)
        return render(request, "public/edit_service.html", context)

    else:
        return error(request, "Invalid object_type")


def review(request):
    if request.method == "POST":
        text = request.POST["text"]
        client_id = request.POST["client_id"]
        client = get_object_or_404(Client, pk=client_id)
        review = Review.objects.create(client=client, text=text)
        review.save()
        return redirect(profile)

def service_picker(request):
    services = None  # Початкове значення для послуг
    if request.method == 'POST':  # Якщо форма була надіслана
        form = ServiceFilterForm(request.POST)
        if form.is_valid():
            skin_type = form.cleaned_data['skin_type']  # Отримуємо тип шкіри
            result = form.cleaned_data['result']  # Отримуємо бажаний результат
            budget = form.cleaned_data.get('budget')  # Отримуємо бюджет, якщо він є

            # Фільтруємо послуги за бюджетом
            services = Service.objects.filter(price__lte=budget) if budget else Service.objects.all()

            # Додаємо фільтри за типом шкіри та результатом
            if skin_type:
                services = services.filter(category__name=skin_type)
            if result:
                services = services.filter(description__icontains=result)

    else:
        form = ServiceFilterForm()  # Якщо це GET-запит, відправляємо порожню форму

    return render(request, 'service_picker/form.html', {'form': form, 'services': services})

def chatbot_picker(request):
    services = Service.objects.none()
    message = None
    debug_info = None

    if request.method == 'POST':
        message = request.POST.get('message', '')
        if message:
            # Змінюємо мітки на українські
            result = classifier(message, candidate_labels=[
                "укладка волосся", "консультація", "стрижка", "масаж обличчя", "суха шкіра", "зволоження"
            ])
            scores = result['scores']
            labels = result['labels']
            debug_info = f"Labels: {labels}, Scores: {scores}"

            categories = []
            for label, score in zip(labels, scores):
                if score > 0.4:
                    if label == "укладка волосся":
                        categories.append("Стрижка та укладка волосся")
                    elif label == "консультація":
                        categories.append("Консультація")
                    elif label == "стрижка":
                        categories.append("Стрижка та укладка волосся")
                    elif label == "масаж обличчя":
                        categories.append("Догляд за обличчям")
                    elif label == "суха шкіра":
                        services = services | Service.objects.filter(description__icontains="суха шкіра")
                    elif label == "зволоження":
                        services = services | Service.objects.filter(description__icontains="зволоження")

            if categories:
                services = services | Service.objects.filter(category__name__in=categories)

    return render(request, 'service_picker/chat.html', {
        'services': services,
        'message': message,
        'debug_info': debug_info
    })