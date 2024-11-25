from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from quiz_site.models import *
import random
import Levenshtein


@login_required
def active_quiz(request):
    users = User.objects.all()
    quiz = Quiz.objects.latest('date_created')
    rounds = quiz.rounds.all()
    question_counter = quiz.question_counter
    current_round = None
    current_index = 0

    # Determine the current round based on the question counter
    for round in rounds:
        round_name = round.question_type
        total_questions = len(quiz.random_numbers.get(round_name, []))
        if question_counter < total_questions:
            current_round = round_name
            break
        question_counter -= total_questions

    if current_round == "Flags":
        current_index = question_counter
        flag_ids = quiz.random_numbers.get("Flags", [])
        current_flag = Flags.objects.get(id=flag_ids[current_index])
        random.seed(f"{quiz.id}-{current_index}")
        all_flags = Flags.objects.exclude(id=current_flag.id).values_list('country', flat=True)
        choices = random.sample(list(all_flags), 5) + [current_flag.country]
        random.shuffle(choices)
        current_question = None
        gk_choices = []
        current_celebrity = None
    elif current_round == "General Knowledge":
        current_index = question_counter
        question_ids = quiz.random_numbers.get("General Knowledge", [])
        current_question = GeneralKnowledge.objects.get(id=question_ids[current_index])
        gk_choices = [current_question.answer, current_question.choice_1, current_question.choice_2, current_question.choice_3]
        random.shuffle(gk_choices)
        current_flag = None
        choices = []
        current_celebrity = None
    elif current_round == "Capital Cities":
        current_index = question_counter
        flag_ids = quiz.random_numbers.get("Capital Cities", [])
        current_flag = Flags.objects.get(id=flag_ids[current_index])
        random.seed(f"{quiz.id}-{current_index}")
        all_flags = Flags.objects.exclude(id=current_flag.id).values_list('capital', flat=True)
        choices = random.sample(list(all_flags), 5) + [current_flag.capital]
        random.shuffle(choices)
        current_question = None
        gk_choices = []
        current_celebrity = None
    elif current_round == "Celebrities":
        current_index = question_counter
        celebrity_ids = quiz.random_numbers.get("Celebrities", [])
        current_celebrity = Celebrities.objects.get(id=celebrity_ids[current_index])
        current_flag = None
        choices = []
        current_question = None
        gk_choices = []
    else:
        current_flag = None
        choices = []
        current_question = None
        gk_choices = []
        current_celebrity = None

    context = {
        'quiz': quiz,
        'current_flag': current_flag,
        'current_flag_index': current_index if current_round in ["Flags", "Capital Cities"] else None,
        'total_flags': len(quiz.random_numbers.get("Flags", [])),
        'choices': choices,
        'current_question': current_question,
        'current_question_index': current_index if current_round == "General Knowledge" else None,
        'total_questions': len(quiz.random_numbers.get("General Knowledge", [])),
        'gk_choices': gk_choices,
        'current_celebrity': current_celebrity,
        'current_round': current_round,
        'users': users,
    }
    return render(request, 'active_quiz.html', context)


@login_required
def check_update(request):
    quiz = Quiz.objects.latest('date_created')
    last_question_counter = request.session.get('last_question_counter', -1)
    if quiz.question_counter != last_question_counter:
        request.session['last_question_counter'] = quiz.question_counter
        return JsonResponse({'update': True})
    return JsonResponse({'update': False})


@login_required
def next_question(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player

        if selected_answer == correct_answer:
            player.player_score = (player.player_score or 0) + 1
            messages.success(request, 'Correct answer! Your score has been updated.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer.')

        player.save()

        if request.user.username == 'david':
            quiz = Quiz.objects.latest('date_created')
            quiz.question_counter += 1
            quiz.save()
            request.session['last_question_counter'] = quiz.question_counter

    return redirect('active_quiz:active_quiz')


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
            messages.success(request, 'Correct answer! Your score has been updated.')
        elif first_name_correct or last_name_correct:
            player.player_score = (player.player_score or 0) + 0.5
            messages.success(request, 'Partially correct answer! You have earned half a point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer.')

        player.save()

        if request.user.username == 'david':
            quiz = Quiz.objects.latest('date_created')
            quiz.question_counter += 1
            quiz.save()

        return redirect('active_quiz:active_quiz')

    return redirect('active_quiz:active_quiz')