from django.shortcuts import render


def login(request):

    context = {
        "title": "Kosyakino - Авторизация",
    }

    return render(request, "users/login.html", context)


def registration(request):

    context = {
        "title": "Kosyakino - Регистрация",
    }

    return render(request, "users/registration.html", context)


def profile(request):

    context = {
        "title": "Kosyakino - Кабинет",
    }

    return render(request, "users/profile.html", context)


def logout(request):

    context = {
        "title": "Kosyakino - Выход",
    }

    return render(request, "users/logout.html", context)
