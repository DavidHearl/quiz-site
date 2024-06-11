from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, reverse
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
    flags = Flags.objects.all()
    flag_form = FlagForm()
    categories = QuestionCategory.objects.all()

    if request.method == 'POST':
        flag_form = FlagForm(request.POST, request.FILES)
        print(flag_form.errors)
        if flag_form.is_valid():
            flag = flag_form.save(commit=False)
            flag.save()
            messages.success(request, 'Flag added successfully.')
            print('Flag added successfully')
            return redirect('flags')

    context = {
        'flags': flags,
        'flag_form': flag_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/flags.html', context)


def edit_flags(request, flag_id):
    users = User.objects.all()
    categories = QuestionCategory.objects.all()
    flag = get_object_or_404(Flags, pk=flag_id)
    flag_form = FlagForm(instance=flag)

    if request.method == 'POST':
        edit_flag_form = FlagForm(request.POST, request.FILES, instance=flag)
        print(edit_flag_form.errors)
        if edit_flag_form.is_valid():
            flag = edit_flag_form.save(commit=False)
            flag.save()
            messages.success(request, 'Area added successfully.')
            print('Flag edited successfully')
            return redirect('flags')

    context = {
        'flags': flags,
        'flag_form': flag_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/flags.html', context)


def logos(request):
    users = User.objects.all()
    logos = Logos.objects.all()
    logo_form = LogoForm()
    categories = QuestionCategory.objects.all()

    if request.method == 'POST':
        logo_form = LogoForm(request.POST, request.FILES)
        print(logo_form.errors)
        if logo_form.is_valid():
            logo = logo_form.save(commit=False)
            logo.save()
            messages.success(request, 'Logo added successfully.')
            print('Logo added successfully')
            return redirect('logos')

    context = {
        'logos': logos,
        'logo_form': logo_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/logos.html', context)


def edit_logos(request, logo_id):
    users = User.objects.all()
    categories = QuestionCategory.objects.all()
    logo = get_object_or_404(Logos, pk=logo_id)
    logo_form = LogoForm(instance=logo)

    if request.method == 'POST':
        edit_logo_form = LogoForm(request.POST, request.FILES, instance=logo)
        print(edit_logo_form.errors)
        if edit_logo_form.is_valid():
            logo = edit_logo_form.save(commit=False)
            logo.save()
            messages.success(request, 'Logo edited successfully.')
            print('Logo edited successfully')
            return redirect('logos')

    context = {
        'logos': logos,
        'logo_form': logo_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/logos.html', context)


def jets(request):
    users = User.objects.all()
    jets = Jets.objects.all()
    jet_form = JetForm()
    categories = QuestionCategory.objects.all()

    if request.method == 'POST':
        jet_form = JetForm(request.POST, request.FILES)
        print(jet_form.errors)
        if jet_form.is_valid():
            jet = jet_form.save(commit=False)
            jet.save()
            messages.success(request, 'Jet added successfully.')
            print('Jet added successfully')
            return redirect('jets')

    context = {
        'jets': jets,
        'jet_form': jet_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/jets.html', context)


def edit_jets(request, jet_id):
    users = User.objects.all()
    categories = QuestionCategory.objects.all()
    jet = get_object_or_404(Jets, pk=jet_id)
    jet_form = JetForm(instance=jet)

    if request.method == 'POST':
        edit_jet_form = JetForm(request.POST, request.FILES, instance=jet)
        print(edit_jet_form.errors)
        if edit_jet_form.is_valid():
            jet = edit_jet_form.save(commit=False)
            jet.save()
            messages.success(request, 'Jet edited successfully.')
            print('Jet edited successfully')
            return redirect('jets')

    context = {
        'jets': jets,
        'jet_form': jet_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/jets.html', context)


def celebrities(request):
    users = User.objects.all()
    celebrities = Celebrities.objects.all()
    celebrity_form = CelebrityForm()
    categories = QuestionCategory.objects.all()

    if request.method == 'POST':
        celebrity_form = CelebrityForm(request.POST, request.FILES)
        print(celebrity_form.errors)
        if celebrity_form.is_valid():
            celebrity = celebrity_form.save(commit=False)
            celebrity.save()
            messages.success(request, 'Celebrity added successfully.')
            print('Celebrity added successfully')
            return redirect('celebrities')

    context = {
        'celebrities': celebrities,
        'celebrity_form': celebrity_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/celebrities.html', context)


def edit_celebrities(request, celebrity_id):
    users = User.objects.all()
    categories = QuestionCategory.objects.all()
    celebrity = get_object_or_404(Celebrities, pk=celebrity_id)
    celebrity_form = CelebrityForm(instance=celebrity)

    if request.method == 'POST':
        edit_celebrity_form = CelebrityForm(request.POST, request.FILES, instance=celebrity)
        print(edit_celebrity_form.errors)
        if edit_celebrity_form.is_valid():
            celebrity = edit_celebrity_form.save(commit=False)
            celebrity.save()
            messages.success(request, 'Celebrity edited successfully.')
            print('Celebrity edited successfully')
            return redirect('celebrities')

    context = {
        'celebrities': celebrities,
        'celebrity_form': celebrity_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/celebrities.html', context)


def movies(request):
    users = User.objects.all()
    movies = Movies.objects.all()
    movie_form = MovieForm()
    categories = QuestionCategory.objects.all()

    if request.method == 'POST':
        movie_form = MovieForm(request.POST, request.FILES)
        print(movie_form.errors)
        if movie_form.is_valid():
            movie = movie_form.save(commit=False)
            movie.save()
            movie_form.save_m2m()
            messages.success(request, 'Movie added successfully.')
            print('Movie added successfully')
            return redirect('movies')

    context = {
        'movies': movies,
        'movie_form': movie_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/movies.html', context)


def edit_movies(request, movie_id):
    users = User.objects.all()
    categories = QuestionCategory.objects.all()
    movie = get_object_or_404(Movies, pk=movie_id)
    movie_form = MovieForm(instance=movie)

    if request.method == 'POST':
        edit_movie_form = MovieForm(request.POST, request.FILES, instance=movie)
        print(edit_movie_form.errors)
        if edit_movie_form.is_valid():
            movie = edit_movie_form.save(commit=False)
            movie.save()
            movie_form.save_m2m()
            messages.success(request, 'Movie edited successfully.')
            print('Movie edited successfully')
            return redirect('movies')

    context = {
        'movies': movies,
        'movie_form': movie_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/movies.html', context)


def location(request):
    users = User.objects.all()
    locations = Location.objects.all()
    location_form = LocationForm()
    categories = QuestionCategory.objects.all()

    if request.method == 'POST':
        location_form = LocationForm(request.POST, request.FILES)
        print(location_form.errors)
        if location_form.is_valid():
            location = location_form.save(commit=False)
            location.save()
            messages.success(request, 'Location added successfully.')
            print('Location added successfully')
            return redirect('location')

    context = {
        'locations': locations,
        'location_form': location_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/location.html', context)


def edit_location(request, location_id):
    users = User.objects.all()
    categories = QuestionCategory.objects.all()
    location = get_object_or_404(Location, pk=location_id)
    location_form = LocationForm(instance=location)

    if request.method == 'POST':
        edit_location_form = LocationForm(request.POST, request.FILES, instance=location)
        print(edit_location_form.errors)
        if edit_location_form.is_valid():
            location = edit_location_form.save(commit=False)
            location.save()
            messages.success(request, 'Location edited successfully.')
            print('Location edited successfully')
            return redirect('location')

    context = {
        'locations': locations,
        'location_form': location_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/location.html', context)