from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from .models import *
from .forms import *


# Create your views here.
def quiz_home(request):
    catagories = QuestionCategory.objects.all()
    countries = Flags.objects.all()

    context = {
        'countries': countries,
        'catagories': catagories
    }

    return render(request, 'quiz_site/quiz_home.html', context)


def flags(request):
    users = User.objects.all()
    countries = Flags.objects.all()
    flag_form = FlagForm()


    if request.method == 'POST':
        flag_form = FlagForm(request.POST, request.FILES)
        print(flag_form.errors)
        if flag_form.is_valid():
            flag = flag_form.save(commit=False)
            flag.save()
            messages.success(request, 'Area added successfully.')
            print('Flag added successfully')
            return redirect('flags')

    context = {
        'countries': countries,
        'flag_form': flag_form,
        'users': users,
    }

    return render(request, 'quiz_site/flags.html', context)


def logos(request):
    logos = Logos.objects.all()
    logo_form = LogoForm()

    if request.method == 'POST':
        logo_form = LogoForm(request.POST, request.FILES)
        print(logo.errors)
        if logo_form.is_valid():
            logo = logo_form.save(commit=False)
            logo.save()
            messages.success(request, 'Area added successfully.')
            print('Logo added successfully')
            return redirect('Logo')

    context = {
        'logos': logos,
        'logo_form': logo_form,
    }

    return render(request, 'quiz_site/logos.html', context)
