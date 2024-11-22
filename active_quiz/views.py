from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from quiz_site.models import *
import random


def active_quiz(request):
    quiz = Quiz.objects.latest('date_created')
    # Get the total number of questions in each round
    total_flags = len(quiz.random_numbers.get("Flags", []))
    total_gk = len(quiz.random_numbers.get("General Knowledge", []))
    # Determine the current round based on the question counter
    if quiz.question_counter < total_flags:
        current_round = "Flags"
    elif quiz.question_counter < total_flags + total_gk:
        current_round = "General Knowledge"
        # Reset gk_answered when transitioning to General Knowledge round
        if request.session.get('last_round') != "General Knowledge":
            request.session['gk_answered'] = False
    else:
        current_round = None
    # Store the current round in the session
    request.session['last_round'] = current_round
    # Get the current question index within the current round
    if current_round == "Flags":
        current_index = quiz.question_counter % total_flags
        flag_ids = quiz.random_numbers.get("Flags", [])
        current_flag = Flags.objects.get(id=flag_ids[current_index])
        random.seed(f"{quiz.id}-{current_index}")
        all_flags = Flags.objects.exclude(id=current_flag.id).values_list('country', flat=True)
        choices = random.sample(list(all_flags), 5) + [current_flag.country]
        random.shuffle(choices)
        current_question = None
        gk_choices = []
    elif current_round == "General Knowledge":
        current_index = (quiz.question_counter - total_flags) % total_gk
        question_ids = quiz.random_numbers.get("General Knowledge", [])
        current_question = GeneralKnowledge.objects.get(id=question_ids[current_index])
        gk_choices = [current_question.answer, current_question.choice_1, current_question.choice_2, current_question.choice_3]
        random.shuffle(gk_choices)
        current_flag = None
        choices = []
    else:
        current_flag = None
        choices = []
        current_question = None
        gk_choices = []
    context = {
        'quiz': quiz,
        'current_flag': current_flag,
        'current_flag_index': current_index if current_round == "Flags" else None,
        'total_flags': total_flags,
        'choices': choices,
        'current_question': current_question,
        'current_question_index': current_index if current_round == "General Knowledge" else None,
        'total_questions': total_gk,
        'gk_choices': gk_choices,
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
def next_flag(request):
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
def next_general_knowledge(request):
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

