from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.http import HttpResponse
from django.contrib import messages
from paradis.models import Master, Client

# Create your views here.


def register_client(request):
    if request.method == "POST":
        phone_number = request.POST["phone_number"]
        address = request.POST["address"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        photo = request.FILES.get("file")
        if password == confirm_password:
            if User.objects.filter(username=email).exists():
                messages.info(request, "User exists")
            else:
                user = User.objects.create_user(username=email, password=password)
                user.save()
                user = auth.authenticate(username=email, password=password)
                auth.login(request, user)

                client = Client.objects.create(
                    full_name=username,
                    email=email,
                    photo=photo,
                    address=address,
                    user=user,
                    phone_number=phone_number,
                )
                client.save()
        else:
            pass_err = "Password are not the same"
            return render(
                request, "authorization/register_client.html", {"pass_err": pass_err}
            )
        return redirect("/")
    else:
        return render(request, "authorization/register_client.html")


def register_master(request):
    if request.method == "POST":
        phone_number = request.POST["phone_number"]
        address = request.POST["address"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        photo = request.FILES.get("file")
        if password == confirm_password:
            if User.objects.filter(username=email).exists():
                messages.info(request, "User exists")
            else:
                user = User.objects.create_user(username=email, password=password)
                user.save()
                user = auth.authenticate(username=email, password=password)
                auth.login(request, user)

                master = Master.objects.create(
                    full_name=username,
                    email=email,
                    photo=photo,
                    address=address,
                    user=user,
                    phone_number=phone_number,
                )
                master.save()
        else:
            pass_err = "Password are not the same"
            return render(
                request, "authorization/register_master.html", {"pass_err": pass_err}
            )
        return redirect("/")
    else:
        return render(request, "authorization/register_master.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username, password=password)
        if user != None:
            try:
                _user = Master.objects.get(user=user)
                if _user.is_confirmed == False:
                    context = {
                        "errors": [
                            "You are not confirmed master. Please contact with the administrator.",
                        ],
                    }
                    return render(request, "public/404.html", context)
                else:
                    auth.login(request, user)
                    return redirect("/")
            except Exception:
                auth.login(request, user)
                return redirect("/")
        else:
            return redirect("login")
    else:
        return render(request, "authorization/login.html")


def logout(request):
    auth.logout(request)
    return redirect("/")
