from django.db.models import Count
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, reverse
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from .models import *
from .forms import *
import random


# Create your views here.
def quiz_home(request):
    users = User.objects.all()
    rounds = Rounds.objects.all()
    quiz = Quiz.objects.all()
    quiz_selection_form = QuizSelectionForm()

    if request.method == 'POST':
        quiz_selection_form = QuizSelectionForm(request.POST)
        if quiz_selection_form.is_valid():
            quiz = Quiz.objects.create(quiz_name=quiz_selection_form.cleaned_data['quiz_name'])
            quiz.players.set(quiz_selection_form.cleaned_data['users'])
            quiz.rounds.set(quiz_selection_form.cleaned_data['rounds'])
            quiz.save()

            # Add question functions here
            print('Adding Questions...')
            add_flag_questions(request)
            # add_general_knowledge_questions(request)
            # add_true_or_false_questions(request)
            # add_logo_questions(request)
            # add_jet_questions(request)
            # add_celebrity_questions(request)
            # add_movie_questions(request)
            # add_location_questions(request)
            
            return redirect('active_quizzes')
        else:
            print(quiz_selection_form.errors)
    else:
        quiz_selection_form = QuizSelectionForm()

    context = {
        'rounds': rounds,
        'quiz': quiz,
        'quiz_selection_form': quiz_selection_form,
        'users': users,
    }

    return render(request, 'quiz_site/quiz_home.html', context)


def active_quizzes(request):
    quiz = Quiz.objects.latest('date_created')
    questions = Questions.objects.filter(quiz=quiz)

    context = {
        'quiz': quiz,
        'questions': questions,
    }

    return render(request, 'quiz_site/active_quiz.html', context)

# -------------------------------------------------------------------------------
# -------------------------- Add Question Functions -----------------------------
# -------------------------------------------------------------------------------
def add_flag_questions(request):
    quiz = Quiz.objects.latest('date_created')
    flags_round_exists = quiz.rounds.filter(question_type="Flags").exists()

    if flags_round_exists:
        # Ensure there is a Questions instance for the quiz
        questions, created = Questions.objects.get_or_create(quiz=quiz)

        # Efficiently select 10 random flag questions if the Flags model is large
        count = Flags.objects.aggregate(count=Count('id'))['count']
        random_indexes = sorted([random.randint(0, count - 1) for _ in range(10)])
        flag_questions = [Flags.objects.all()[index] for index in random_indexes]

        for flag_question in flag_questions:
            questions.flags.add(flag_question)

        print('Flag questions added successfully')
    else:
        print('No Flags round for this quiz')

    return redirect('active_quizzes')
    
# -------------------------------------------------------------------------------
# ----------------------------- Question Models ---------------------------------
# -------------------------------------------------------------------------------

def general_knowledge(request):
    users = User.objects.all()
    general_knowledge = GeneralKnowledge.objects.all()
    general_knowledge_form = GeneralKnowledgeForm()

    if request.method == 'POST':
        general_knowledge_form = GeneralKnowledgeForm(request.POST, request.FILES)
        print(general_knowledge_form.errors)
        if general_knowledge_form.is_valid():
            general_knowledge = general_knowledge_form.save(commit=False)
            general_knowledge.save()
            messages.success(request, 'Question added successfully.')
            print('Question added successfully')
            return redirect('general_knowledge')
        else:
            print(general_knowledge_form.errors)

    context = {
        'general_knowledge': general_knowledge,
        'general_knowledge_form': general_knowledge_form,
        'users': users,
    }

    return render(request, 'quiz_site/general_knowledge.html', context)


def edit_general_knowledge(request, question_id):
    users = User.objects.all()
    question = get_object_or_404(GeneralKnowledge, pk=question_id)
    general_knowledge_form = GeneralKnowledgeForm(instance=question)

    if request.method == 'POST':
        edit_general_knowledge_form = GeneralKnowledgeForm(request.POST, request.FILES, instance=question)
        print(edit_general_knowledge_form.errors)
        if edit_general_knowledge_form.is_valid():
            question = edit_general_knowledge_form.save(commit=False)
            question.save()
            messages.success(request, 'Question edited successfully.')
            print('Question edited successfully')
            return redirect('general_knowledge')

    context = {
        'general_knowledge': general_knowledge,
        'general_knowledge_form': general_knowledge_form,
        'users': users,
    }

    return render(request, 'quiz_site/general_knowledge.html', context)


def true_or_false(request):
    users = User.objects.all()
    true_or_false = TrueOrFalse.objects.all()
    true_or_false_form = TrueOrFalseForm()

    if request.method == 'POST':
        true_or_false_form = TrueOrFalseForm(request.POST, request.FILES)
        print(true_or_false_form.errors)
        if true_or_false_form.is_valid():
            true_or_false = true_or_false_form.save(commit=False)
            true_or_false.save()
            messages.success(request, 'Question added successfully.')
            print('Question added successfully')
            return redirect('true_or_false')

    context = {
        'true_or_false': true_or_false,
        'true_or_false_form': true_or_false_form,
        'users': users,
    }

    return render(request, 'quiz_site/true_or_false.html', context)


def edit_true_or_false(request, question_id):
    users = User.objects.all()
    question = get_object_or_404(TrueOrFalse, pk=question_id)
    true_or_false_form = TrueOrFalseForm(instance=question)

    if request.method == 'POST':
        edit_true_or_false_form = TrueOrFalseForm(request.POST, request.FILES, instance=question)
        print(edit_true_or_false_form.errors)
        if edit_true_or_false_form.is_valid():
            question = edit_true_or_false_form.save(commit=False)
            question.save()
            messages.success(request, 'Question edited successfully.')
            print('Question edited successfully')
            return redirect('true_or_false')

    context = {
        'true_or_false': true_or_false,
        'true_or_false_form': true_or_false_form,
        'users': users,
    }

    return render(request, 'quiz_site/true_or_false.html', context)
    

def flags(request):
    users = User.objects.all()
    flags = Flags.objects.all()
    flag_form = FlagForm()

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
    }

    return render(request, 'quiz_site/flags.html', context)


def edit_flags(request, flag_id):
    users = User.objects.all()
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
    }

    return render(request, 'quiz_site/flags.html', context)


def logos(request):
    users = User.objects.all()
    logos = Logos.objects.all()
    logo_form = LogoForm()

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
    }

    return render(request, 'quiz_site/logos.html', context)


def edit_logos(request, logo_id):
    users = User.objects.all()
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
    }

    return render(request, 'quiz_site/logos.html', context)


def jets(request):
    users = User.objects.all()
    jets = Jets.objects.all()
    jet_form = JetForm()

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
    }

    return render(request, 'quiz_site/jets.html', context)


def edit_jets(request, jet_id):
    users = User.objects.all()
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
    }

    return render(request, 'quiz_site/jets.html', context)


def celebrities(request):
    users = User.objects.all()
    celebrities = Celebrities.objects.all()
    celebrity_form = CelebrityForm()

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
    }

    return render(request, 'quiz_site/celebrities.html', context)


def edit_celebrities(request, celebrity_id):
    users = User.objects.all()
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
    }

    return render(request, 'quiz_site/celebrities.html', context)


def movies(request):
    users = User.objects.all()
    movies = Movies.objects.all()
    movie_form = MovieForm()

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
    }

    return render(request, 'quiz_site/movies.html', context)


def edit_movies(request, movie_id):
    users = User.objects.all()
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
    }

    return render(request, 'quiz_site/movies.html', context)


def locations(request):
    users = User.objects.all()
    locations = Locations.objects.all()
    location_form = LocationForm()

    if request.method == 'POST':
        location_form = LocationForm(request.POST, request.FILES)
        print(location_form.errors)
        if location_form.is_valid():
            location = location_form.save(commit=False)
            location.save()
            messages.success(request, 'Location added successfully.')
            print('Location added successfully')
            return redirect('locations')

    context = {
        'locations': locations,
        'location_form': location_form,
        'users': users,
    }

    return render(request, 'quiz_site/location.html', context)


def edit_locations(request, location_id):
    users = User.objects.all()
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
            return redirect('locations')
        else:
            print(edit_location_form.errors)

    context = {
        'locations': locations,
        'location_form': location_form,
        'users': users,
    }

    return render(request, 'quiz_site/location.html', context)