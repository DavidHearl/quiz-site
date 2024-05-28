from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import *
from .forms import *


# Create your views here.
def quiz_home(request):
    catagories = QuestionCategory.objects.all()
    countries = GuessTheFlag.objects.all()

    context = {
        'countries': countries,
        'catagories': catagories
    }

    return render(request, 'quiz_site/quiz_home.html', context)


def flag(request):
    countries = GuessTheFlag.objects.all()

    if request.method == 'POST':
        flag_form = FlagForm(request.POST)
        print(flag_form.errors)
        if flag_form.is_valid():
            flag = flag_form.save(commit=False)
            flag.save()
            messages.success(request, 'Area added successfully.')
            print('Flag added successfully')
            return redirect('flag')

    context = {
        'countries': countries,
        'flag_form': FlagForm()
    }

    return render(request, 'quiz_site/guess_the_flag.html', context)
