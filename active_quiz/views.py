from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from quiz_site.models import *
import random


def active_quiz(request):
    quiz = Quiz.objects.latest('date_created')

    flag_ids = quiz.random_numbers.get("Flags", [])
    flags = [Flags.objects.get(id=flag_id) for flag_id in flag_ids]
    current_flag_index = quiz.question_counter % len(flags) if flags else 0
    request.session['current_flag_index'] = current_flag_index

    current_flag = flags[current_flag_index] if flags else None
    if current_flag:
        random.seed(f"{quiz.id}-{current_flag_index}")
        all_flags = Flags.objects.exclude(id=current_flag.id).values_list('country', flat=True)
        choices = random.sample(list(all_flags), 5) + [current_flag.country]
        random.shuffle(choices)
    else:
        choices = []
    context = {
        'quiz': quiz,
        'current_flag': current_flag,
        'current_flag_index': current_flag_index,
        'total_flags': len(flags),
        'choices': choices,
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
            current_flag_index = request.session.get('current_flag_index', 0)
            current_flag_index += 1
            request.session['current_flag_index'] = current_flag_index

            quiz = Quiz.objects.latest('date_created')
            quiz.question_counter += 1
            quiz.save()
            request.session['last_question_counter'] = quiz.question_counter

    return redirect('active_quiz:active_quiz')


@login_required
def previous_flag(request):
    current_flag_index = request.session.get('current_flag_index', 0)
    current_flag_index = max(0, current_flag_index - 1)
    request.session['current_flag_index'] = current_flag_index

    if request.user.username == 'david':
        quiz = Quiz.objects.latest('date_created')
        quiz.question_counter = max(0, quiz.question_counter - 1)
        quiz.save()
        request.session['last_question_counter'] = quiz.question_counter

    return redirect('active_quiz:active_quiz')