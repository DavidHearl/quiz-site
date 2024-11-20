from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from quiz_site.models import *
import random

def active_quiz(request):
    quiz = Quiz.objects.latest('date_created')

    flag_ids = quiz.random_numbers.get("Flags", [])
    flags = [Flags.objects.get(id=flag_id) for flag_id in flag_ids]
    current_flag_index = request.session.get('current_flag_index', 0)
    if current_flag_index >= len(flags):
        current_flag_index = 0
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
def next_flag(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        if selected_answer == correct_answer:
            player = request.user.player
            player.player_score = (player.player_score or 0) + 1
            player.save()
            messages.success(request, 'Correct answer! Your score has been updated.')
        else:
            messages.error(request, 'Incorrect answer.')
    
    current_flag_index = request.session.get('current_flag_index', 0)
    current_flag_index += 1
    request.session['current_flag_index'] = current_flag_index

    if request.user.username == 'david':
        quiz = Quiz.objects.latest('date_created')
        quiz.question_counter += 1
        quiz.save()

    return redirect('active_quiz')

@login_required
def previous_flag(request):
    current_flag_index = request.session.get('current_flag_index', 0)
    current_flag_index = max(0, current_flag_index - 1)
    request.session['current_flag_index'] = current_flag_index

    if request.user.username == 'david':
        quiz = Quiz.objects.latest('date_created')
        quiz.question_counter = max(0, quiz.question_counter - 1)
        quiz.save()

    return redirect('active_quiz')