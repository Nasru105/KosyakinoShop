from email import message
from django.contrib import auth, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from users.forms import UserLoginForm, UserRegistrationForm, ProfileForm


def login(request):

    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                messages.success(request, f"{username}, Вы вошли в аккаунт")
                return HttpResponseRedirect(reverse("main:index"))
    else:
        form = UserLoginForm()

    context = {
        "title": "Kosyakino - Авторизация",
        "form": form,
    }

    return render(request, "users/login.html", context)


def registration(request):

    if request.method == "POST":
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = form.instance
            auth.login(request, user)
            messages.success(
                request,
                f"{user.username}, Вы успешно зарегистрировались и вошли в аккаунт",
            )
            return HttpResponseRedirect(reverse("main:index"))
    else:
        form = UserRegistrationForm()
    context = {
        "title": "Kosyakino - Регистрация",
        "form": form,
    }

    return render(request, "users/registration.html", context)


@login_required
def profile(request):

    if request.method == "POST":
        form = ProfileForm(
            data=request.POST, instance=request.user, files=request.FILES
        )
        if form.is_valid():
            form.save()
            messages.success(request, f"Профиль успешно обновлен")
            return HttpResponseRedirect(reverse("users:profile"))

    else:
        form = ProfileForm(instance=request.user)

    context = {
        "title": "Kosyakino - Кабинет",
        "form": form,
    }
    return render(request, "users/profile.html", context)


def logout(request):
    messages.success(request, f"{request.user.username}, Вы вышли из аккаунта")
    auth.logout(request)
    return redirect(reverse("main:index"))
