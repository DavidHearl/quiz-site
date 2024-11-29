from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from quiz_site.models import *
import random
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
        print(request, "No current round found.")
        return redirect('quiz_home')

    round_handlers = {
        "Flags": handle_flags_round,
        "General Knowledge": handle_general_knowledge_round,
        "Capital Cities": handle_capital_cities_round,
        "Celebrities": handle_celebrities_round,
        "Logos": handle_logos_round,
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
    obfuscated_name = "*" * len(current_logo.company)
    return {
        'current_logo': current_logo,
        'obfuscated_name': obfuscated_name,
    }