from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from quiz_site.models import *
import random
from datetime import datetime
import Levenshtein


'''
Main function that controls the active quiz page.
'''
@login_required
def active_quiz(request):
    users = User.objects.all()
    quiz = Quiz.objects.latest('date_created')
    rounds = quiz.rounds.all()
    question_counter = quiz.question_counter

    current_round = None
    current_index = 0

    for round in rounds:
        round_name = round.question_type
        total_questions = len(quiz.random_numbers.get(round_name, []))
        if question_counter < total_questions:
            current_round = round_name
            current_index = question_counter
            break
        question_counter -= total_questions

    if current_round is None:
        return redirect('active_quiz:quiz_results')

    round_handlers = {
        "Flags": handle_flags_round,
        "General Knowledge": handle_general_knowledge_round,
        "Capital Cities": handle_capital_cities_round,
        "Celebrities": handle_celebrities_round,
        "Logos": handle_logos_round,
        "True or False": handle_true_or_false_round,
        "Guess the Celebrity Age": handle_celebrity_age_round,
        "Movie Release Dates": handle_movie_release_dates_round,
    }

    context = {
        'quiz': quiz,
        'current_round': current_round,
        'current_index': current_index,
        'current_flag': None,
        'current_question': None,
        'gk_choices': [],
        'current_celebrity': None, 
        'choices': [],
    }

    if current_round in round_handlers:
        round_context = round_handlers[current_round](quiz, current_index)
        context.update(round_context)

    return render(request, 'active_quiz.html', context)


'''
Function to update the page for a user when the quiz master has moved on to the next question.
'''
@login_required
def check_update(request):
    quiz = Quiz.objects.latest('date_created')
    players = quiz.players.all()

    last_question_counter = request.session.get('last_question_counter', -1)
    if quiz.question_counter != last_question_counter:
        request.session['last_question_counter'] = quiz.question_counter
        return JsonResponse({'update': True})

    for user in players:
        player = Player.objects.get(user=user)
        update_checker = player.page_updates - quiz.question_counter
        if update_checker != 1:
            if player.question_answered != 0:
                player.page_updates += 1
                player.save()
                return JsonResponse({'update': True})

    return JsonResponse({'update': False})    
  

@login_required
def quiz_results(request):
    quiz = Quiz.objects.latest('date_created')
    players = Player.objects.filter(player_score__gt=0).order_by('-player_score')
    winner = players.first() if players else None
    context = {
        'quiz': quiz,
        'players': players,
        'winner': winner,
    }
    return render(request, 'results.html', context)


# --------------------------------------------------------------------- #
# ---------------------- Next Question Functions ---------------------- #
# --------------------------------------------------------------------- #

'''
Function to move on to the next question in the quiz.
This function is designed for multiple choice questions.
'''
@login_required
def next_question(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        if selected_answer == correct_answer:
            player.player_score = (player.player_score or 0) + 1
            player.question_answered = 1  # Correct
            messages.success(request, 'Correct answer! Your score has been updated.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer.')
        player.save()
        if request.user.username == 'david':
            quiz = Quiz.objects.latest('date_created')
            quiz.question_counter += 1
            quiz.save()
            request.session['last_question_counter'] = quiz.question_counter
            # Reset all players' question_answered to 0 (Not Answered)
            for p in Player.objects.all():
                p.question_answered = 0
                p.save()
    return redirect('active_quiz:active_quiz')


'''
Function to move on to the next question in the quiz.
This function is designed for the celebrities round which has two text inputs which require validation
'''
@login_required
def next_celebrity(request):
    if request.method == 'POST':
        selected_first_name = request.POST.get('first_name', '').strip().lower()
        selected_last_name = request.POST.get('last_name', '').strip().lower()
        correct_first_name = request.POST.get('correct_first_name', '').strip().lower()
        correct_last_name = request.POST.get('correct_last_name', '').strip().lower()
        player = request.user.player

        def is_acceptable(answer, correct_answer):
            return Levenshtein.distance(answer, correct_answer) <= 2

        first_name_correct = is_acceptable(selected_first_name, correct_first_name)
        last_name_correct = is_acceptable(selected_last_name, correct_last_name)

        if first_name_correct and last_name_correct:
            player.player_score = (player.player_score or 0) + 1
            player.question_answered = 1  # Correct
            messages.success(request, 'Correct answer! Your score has been updated.')
        elif first_name_correct or last_name_correct:
            player.player_score = (player.player_score or 0) + 0.5
            player.question_answered = 1  # Partially correct
            messages.success(request, 'Partially correct answer! You have earned half a point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer.')
        player.save()
        if request.user.username == 'david':
            quiz = Quiz.objects.latest('date_created')
            quiz.question_counter += 1
            quiz.save()
            # Reset all players' question_answered to 0 (Not Answered)
            for p in Player.objects.all():
                p.question_answered = 0
                p.save()
    return redirect('active_quiz:active_quiz')


@login_required
def next_logo(request):
    if request.method == 'POST':
        selected_company = request.POST.get('company', '').strip()
        correct_company = request.POST.get('correct_company', '').strip()
        player = request.user.player

        if request.user.username != 'david':
            if not selected_company or not correct_company:
                messages.error(request, 'Both the selected and correct company names must be provided.')
                return redirect('active_quiz:active_quiz')

            if selected_company.lower() == correct_company.lower():
                player.player_score = (player.player_score or 0) + 1
                player.question_answered = 1  # Correct
                messages.success(request, 'Correct answer! Your score has been updated.')
            else:
                player.incorrect_answers = (player.incorrect_answers or 0) + 1
                player.question_answered = 2  # Incorrect
                messages.error(request, 'Incorrect answer.')
        else:
            player.question_answered = 1  # Correct for 'david'

        player.save()
        if request.user.username == 'david':
            quiz = Quiz.objects.latest('date_created')
            quiz.question_counter += 1
            quiz.save()
            request.session['last_question_counter'] = quiz.question_counter
            # Reset all players' question_answered to 0 (Not Answered)
            for p in Player.objects.all():
                p.question_answered = 0
                p.save()
    return redirect('active_quiz:active_quiz')


@login_required
def next_true_or_false(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        if selected_answer == correct_answer:
            player.player_score = (player.player_score or 0) + 1
            player.question_answered = 1  # Correct
            messages.success(request, 'Correct answer! Your score has been updated.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer.')
        player.save()
        if request.user.username == 'david':
            quiz = Quiz.objects.latest('date_created')
            quiz.question_counter += 1
            quiz.save()
            request.session['last_question_counter'] = quiz.question_counter
            # Reset all players' question_answered to 0 (Not Answered)
            for p in Player.objects.all():
                p.question_answered = 0
                p.save()
    return redirect('active_quiz:active_quiz')


@login_required
def next_celebrity_age(request):
    if request.method == 'POST':
        selected_age = request.POST.get('age')
        correct_age = request.POST.get('correct_age')
        
        if request.user.username != 'david' and (selected_age is None or correct_age is None):
            messages.error(request, 'Both the selected and correct ages must be provided.')
            return redirect('active_quiz:active_quiz')
        
        if selected_age is not None:
            selected_age = int(selected_age)
        correct_age = int(correct_age)
        
        player = request.user.player
        if selected_age == correct_age:
            player.player_score = (player.player_score or 0) + 1
            player.question_answered = 1  # Correct
            messages.success(request, 'Correct answer! Your score has been updated.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer.')
        player.save()
        
        if request.user.username == 'david' or 'next' in request.POST:
            quiz = Quiz.objects.latest('date_created')
            quiz.question_counter += 1
            quiz.save()
            request.session['last_question_counter'] = quiz.question_counter
            # Reset all players' question_answered to 0 (Not Answered)
            for p in Player.objects.all():
                p.question_answered = 0
                p.save()
                
    return redirect('active_quiz:active_quiz')

@login_required
def next_movie_release_date(request):
    if request.method == 'POST':
        selected_year = request.POST.get('year')
        correct_year = request.POST.get('correct_year')
        
        if request.user.username != 'david' and (selected_year is None or correct_year is None):
            messages.error(request, 'Both the selected and correct years must be provided.')
            return redirect('active_quiz:active_quiz')
        
        if selected_year is not None:
            selected_year = int(selected_year)
        correct_year = int(correct_year)
        
        player = request.user.player
        if selected_year == correct_year:
            player.player_score = (player.player_score or 0) + 1
            player.question_answered = 1  # Correct
            messages.success(request, 'Correct answer! Your score has been updated.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer.')
        player.save()
        
        if request.user.username == 'david' or 'next' in request.POST:
            quiz = Quiz.objects.latest('date_created')
            quiz.question_counter += 1
            quiz.save()
            request.session['last_question_counter'] = quiz.question_counter
            # Reset all players' question_answered to 0 (Not Answered)
            for p in Player.objects.all():
                p.question_answered = 0
                p.save()
                
    return redirect('active_quiz:active_quiz')
# --------------------------------------------------------------------- #
# ---------------------- Round Handling Functions ---------------------- #
# --------------------------------------------------------------------- #

def handle_flags_round(quiz, current_index):
    flag_ids = quiz.random_numbers.get("Flags", [])
    current_flag = Flags.objects.get(id=flag_ids[current_index])
    random.seed(f"{quiz.id}-{current_index}")
    all_flags = Flags.objects.exclude(id=current_flag.id).values_list('country', flat=True)
    choices = random.sample(list(all_flags), 5) + [current_flag.country]
    random.shuffle(choices)
    return {
        'current_flag': current_flag,
        'choices': choices,
    }

def handle_general_knowledge_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("General Knowledge", [])
    current_question = GeneralKnowledge.objects.get(id=question_ids[current_index])
    gk_choices = [current_question.answer, current_question.choice_1, current_question.choice_2, current_question.choice_3]
    random.shuffle(gk_choices)
    return {
        'current_question': current_question,
        'gk_choices': gk_choices,
    }

def handle_capital_cities_round(quiz, current_index):
    flag_ids = quiz.random_numbers.get("Capital Cities", [])
    current_flag = Flags.objects.get(id=flag_ids[current_index])
    random.seed(f"{quiz.id}-{current_index}")
    all_flags = Flags.objects.exclude(id=current_flag.id).values_list('capital', flat=True)
    choices = random.sample(list(all_flags), 5) + [current_flag.capital]
    random.shuffle(choices)
    return {
        'current_flag': current_flag,
        'choices': choices,
    }

def handle_celebrities_round(quiz, current_index):
    celebrity_ids = quiz.random_numbers.get("Celebrities", [])
    current_celebrity = Celebrities.objects.get(id=celebrity_ids[current_index])
    return {
        'current_celebrity': current_celebrity,
    }

def handle_logos_round(quiz, current_index):
    logo_ids = quiz.random_numbers.get("Logos", [])
    current_logo = Logos.objects.get(id=logo_ids[current_index])
    obfuscated_name = ''.join('*' if char != ' ' else ' ' for char in current_logo.company)
    return {
        'current_logo': current_logo,
        'obfuscated_name': obfuscated_name,
    }

def handle_true_or_false_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("True or False", [])
    current_question = TrueOrFalse.objects.get(id=question_ids[current_index])
    return {
        'current_question': current_question,
    }

def handle_celebrity_age_round(quiz, current_index):
    celebrity_ids = quiz.random_numbers.get("Guess the Celebrity Age", [])
    current_celebrity = Celebrities.objects.get(id=celebrity_ids[current_index])
    birth_year = current_celebrity.date_of_birth.year
    current_year = datetime.now().year
    correct_age = current_year - birth_year
    
    # Ensure the correct age is within the range of 20 to 100
    correct_age = max(20, min(correct_age, 100))
    
    # Use a seed to ensure the same answer set for each user
    random.seed(f"{quiz.id}-{current_index}")
    
    # Decide a position for the correct age (e.g., random position within 7 options)
    correct_position = random.randint(0, 6)
    
    # Generate age options with 3 years apart
    age_options = []
    for i in range(7):
        age = correct_age + 3 * (i - correct_position)
        age = max(20, min(age, 100))  # Ensure age is within the range of 20 to 100
        age_options.append(age)
    
    # Ensure the correct age is included in the options
    if correct_age not in age_options:
        age_options[correct_position] = correct_age
    
    return {
        'current_celebrity': current_celebrity,
        'correct_age': correct_age,
        'age_options': age_options,
    }

def handle_movie_release_dates_round(quiz, current_index):
    movie_ids = quiz.random_numbers.get("Movie Release Dates", [])
    current_movie = Movies.objects.get(id=movie_ids[current_index])
    release_year = current_movie.release_date.year
    current_year = datetime.now().year
    
    # Use a seed to ensure the same answer set for each user
    random.seed(f"{quiz.id}-{current_index}")
    
    # Decide a position for the correct release year (e.g., random position within 7 options)
    correct_position = random.randint(0, 6)
    
    # Determine the year interval based on the release year
    year_interval = 2 if release_year > 2000 else 3
    
    # Generate year options with the specified interval
    year_options = []
    for i in range(7):
        year = release_year + year_interval * (i - correct_position)
        if year > current_year:
            year = current_year - (year - current_year)
        year_options.append(year)
    
    # Ensure the correct release year is included in the options
    if release_year not in year_options:
        year_options[correct_position] = release_year
    
    return {
        'current_movie': current_movie,
        'correct_year': release_year,
        'year_options': year_options,
    }