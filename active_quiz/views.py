from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from quiz_site.models import *
import random
from datetime import datetime
import Levenshtein
from Levenshtein import distance as levenshtein_distance


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
        return redirect('active_quiz:round_results')

    round_handlers = {
        "Flags": handle_flags_round,
        "General Knowledge": handle_general_knowledge_round,
        "Capital Cities": handle_capital_cities_round,
        "Celebrities": handle_celebrities_round,
        "Logos": handle_logos_round,
        "True or False": handle_true_or_false_round,
        "Celebrity Age": handle_celebrity_age_round,
        "Movie Release Dates": handle_movie_release_dates_round,
        "Who is the Oldest": handle_who_is_the_oldest_round,
        "Who is the Imposter": handle_who_is_the_imposter_round,
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

    return JsonResponse({'update': False})


@login_required
def print_player_data(request):
    players = Player.objects.all()
    player_data = []
    for player in players:
        player_data.append({
            'username': player.user.username,
            'score': player.player_score,
            'incorrect_answers': player.incorrect_answers,
            'question_answered': player.question_answered,
        })
    return JsonResponse({'players': player_data})


@login_required
def round_results(request):
    quiz = Quiz.objects.latest('date_created')
    players = quiz.players.all()
    
    # Get the last round name from quiz.correct_answers
    if quiz.correct_answers:
        current_round = list(quiz.correct_answers.keys())[-1]
    else:
        current_round = None

    question_counter = quiz.question_counter
    rounds = quiz.rounds.all()
    total_questions = len(rounds) * 10

    # Determine the start and end indices for the last 10 questions
    start_index = max(0, question_counter - 10)
    end_index = question_counter

    correct_answers = quiz.correct_answers.get(current_round, [])  # Get correct answers for the current round
    last_10_answers = correct_answers[-10:]

    # Combine answers and points for the current round
    combined_player_data = {}
    for player in players:
        combined_data = []
        answers = player.player.answers.get(current_round, [])
        points = player.player.points.get(current_round, [])
        for i, answer in enumerate(answers):
            combined_data.append({
                'type': 'answer',
                'value': answer,
                'point': points[i] if i < len(points) else 0
            })
        combined_player_data[player] = combined_data

    context = {
        'quiz': quiz,
        'players': players,
        'current_round': current_round,
        'correct_answers': correct_answers,
        'combined_player_data': combined_player_data,
        'last_10_answers': last_10_answers,
    }
    return render(request, 'round_results.html', context)


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


@login_required
def next_round(request):
    quiz = Quiz.objects.latest('date_created')
    rounds = quiz.rounds.all()

    total_questions = len(rounds) * 10
    question_counter = quiz.question_counter

    if question_counter >= total_questions:
        return redirect('active_quiz:quiz_results') 

    return redirect('active_quiz:active_quiz')


@login_required
def update_score(request):
    player_id = request.POST.get('player_id')
    score_change = request.POST.get('score_change')
    
    try:
        score_change = float(score_change)
    except ValueError:
        # Handle the error appropriately
        return redirect('active_quiz:round_results')

    player = get_object_or_404(Player, id=player_id)
    player_score = player.player_score
    player_score += score_change
    player.player_score = round(player_score, 1)

    player.save()
    
    return redirect('active_quiz:round_results')

# --------------------------------------------------------------------- #
# ------------------------- Utility Functions ------------------------- #
# --------------------------------------------------------------------- #

def iterate_next_question(request):
    quiz = Quiz.objects.latest('date_created')
    rounds = quiz.rounds.all()

    total_questions = sum(len(quiz.random_numbers.get(round.question_type, [])) for round in rounds)
    current_round = None

    if request.user.username == 'david':
        quiz.question_counter += 1
        quiz.save()
        
        for round in rounds:
            round_name = round.question_type
            round_questions = len(quiz.random_numbers.get(round_name, []))
            quiz.question_counter -= round_questions
        
        # Reset all players' question_answered to 0 (Not Answered)
        for player in Player.objects.all():
            player.question_answered = 0
            player.save()

    # Set the current round for all users
    for round in rounds:
        round_name = round.question_type
        round_questions = len(quiz.random_numbers.get(round_name, []))
        if quiz.question_counter <= round_questions:
            current_round = round_name
            break
        quiz.question_counter -= round_questions

    # Ensure "david" has the same current_round as everyone else
    if request.user.username == 'david':
        request.session['current_round'] = current_round
    else:
        request.session['current_round'] = current_round

    # Check if the current round has ended
    if request.user.username != 'david' and quiz.question_counter % 10 == 9 and quiz.question_counter != 0 and quiz.question_counter <= total_questions:
        return redirect('active_quiz:round_results')
    elif request.user.username == 'david' and quiz.question_counter % 10 == 0 and quiz.question_counter != 0 and quiz.question_counter <= total_questions:
        return redirect('active_quiz:round_results')

    # Default return for all users
    return redirect('active_quiz:active_quiz')
        
        

# --------------------------------------------------------------------- #
# ---------------------- Next Question Functions ---------------------- #
# --------------------------------------------------------------------- #

@login_required
def next_flag(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = (player.player_score or 0) + 1
            player.question_answered = 1  # Correct
            score = 1
            messages.success(request, 'Correct answer! You have earned 1 point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        # Record the answer and score
        round_name = "Flags"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

    return iterate_next_question(request)


@login_required
def next_general_knowledge(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = (player.player_score or 0) + 1
            player.question_answered = 1  # Correct
            score = 1
            messages.success(request, 'Correct answer! You have earned 1 point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        # Record the answer and score
        round_name = "General Knowledge"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

    return iterate_next_question(request)


@login_required
def next_capital_city(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = (player.player_score or 0) + 1
            player.question_answered = 1  # Correct
            score = 1
            messages.success(request, 'Correct answer! You have earned 1 point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        # Record the answer and score
        round_name = "Capital Cities"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

    return iterate_next_question(request)


def next_celebrity(request):
    if request.method == 'POST':
        selected_first_name = request.POST.get('first_name', '').strip().lower()
        selected_last_name = request.POST.get('last_name', '').strip().lower()
        correct_first_name = request.POST.get('correct_first_name', '').strip().lower()
        correct_last_name = request.POST.get('correct_last_name', '').strip().lower()
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        def is_acceptable(answer, correct_answer):
            return Levenshtein.distance(answer, correct_answer) <= 2

        first_name_correct = is_acceptable(selected_first_name, correct_first_name)
        last_name_correct = is_acceptable(selected_last_name, correct_last_name)

        if first_name_correct and last_name_correct:
            player.player_score = (player.player_score or 0) + 1
            player.question_answered = 1  # Correct
            score = 1
            messages.success(request, 'Correct answer! You have earned 1 point.')
        elif first_name_correct or last_name_correct:
            player.player_score = (player.player_score or 0) + 0.5
            player.question_answered = 3  # Partially correct
            score = 0.5
            messages.success(request, 'Partially correct answer! You have earned 0.5 points.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer.')

        # Record the answer and score
        round_name = "Celebrities"
        player.answers.setdefault(round_name, []).append(f"{selected_first_name} {selected_last_name}")
        player.points.setdefault(round_name, []).append(score)
        player.save()

        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(f"{correct_first_name} {correct_last_name}")
            quiz.save()

    return iterate_next_question(request)


@login_required
def next_logo(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('company')
        correct_answer = request.POST.get('correct_company')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')
        
        # Initialize score
        score = 0
        
        if request.user.username != 'david':
            if levenshtein_distance(selected_answer.lower(), correct_answer.lower()) <= 1:
                player.player_score = (player.player_score or 0) + 1
                player.question_answered = 1  # Correct
                score = 1
                messages.success(request, 'Correct answer! You earned 1 point.')
            else:
                player.incorrect_answers = (player.incorrect_answers or 0) + 1
                player.question_answered = 2  # Incorrect
                score = 0
                messages.error(request, 'Incorrect answer. No points earned.')
        
        # Record the answer and score
        round_name = "Logos"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()
        
        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()
        
    return iterate_next_question(request)


@login_required
def next_true_or_false(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        # Initialize score
        score = 0

        if request.user.username != 'david':
            if selected_answer == correct_answer:
                player.player_score = (player.player_score or 0) + 1
                player.question_answered = 1  # Correct
                score = 1
                messages.success(request, 'Correct answer! You have earned 1 point.')
            else:
                player.incorrect_answers = (player.incorrect_answers or 0) + 1
                player.question_answered = 2  # Incorrect
                messages.error(request, 'Incorrect answer. No points earned.')

            # Record the answer and score
            round_name = "True or False"
            player.answers.setdefault(round_name, []).append(selected_answer)
            player.points.setdefault(round_name, []).append(score)
            player.save()

            # Save the correct answer to quiz.correct_answers if not already saved
            if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
                quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
                quiz.save()

    return iterate_next_question(request)


@login_required
def next_celebrity_age(request):
    if request.method == 'POST':
        quiz = Quiz.objects.latest('date_created')
        selected_age = request.POST.get('age')
        correct_age = request.POST.get('correct_age')
        if request.user.username != 'david' and (selected_age is None or correct_age is None):
            messages.error(request, 'Both the selected and correct ages must be provided.')
            return redirect('active_quiz:active_quiz')
        if selected_age is not None:
            selected_age = int(selected_age)
        correct_age = int(correct_age)
        player = request.user.player
        age_difference = abs(selected_age - correct_age)
        # Award points based on how close the user was to the correct age
        if age_difference == 0:
            score = 2
        elif age_difference <= 1:
            score = 1.5
        elif age_difference <= 2:
            score = 1.2
        elif age_difference <= 4:
            score = 0.7
        elif age_difference <= 6:
            score = 0.3
        elif age_difference <= 8:
            score = 0.1
        else:
            score = 0
        
        if request.user.username != 'david':
            player.player_score = (player.player_score or 0) + score
            if score >= 1:
                player.question_answered = 1
            elif 0 < score < 1:
                player.question_answered = 3
            else:
                player.question_answered = 2

            # Logic to inform the player of their results
            if score > 0:
                messages.success(request, f'You were {age_difference} years off! You have earned {score} points.')
            else:
                messages.error(request, f'You were {age_difference} years off. No points earned.')
        
        # Record the answer and score
        round_name = "Celebrity Age"
        player.answers.setdefault(round_name, []).append(selected_age)
        player.points.setdefault(round_name, []).append(score)
        player.save()
        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_age)
            quiz.save()

    return iterate_next_question(request)


@login_required
def next_movie_release_date(request):
    if request.method == 'POST':
        quiz = Quiz.objects.latest('date_created')
        selected_year = request.POST.get('year')
        correct_year = request.POST.get('correct_year')
        
        if request.user.username != 'david' and (selected_year is None or correct_year is None):
            messages.error(request, 'Both the selected and correct years must be provided.')
            return redirect('active_quiz:active_quiz')
        
        if selected_year is not None:
            selected_year = int(selected_year)
        correct_year = int(correct_year)
        
        player = request.user.player
        year_difference = abs(selected_year - correct_year)
        
        # Award points based on how close the user was to the correct year
        if year_difference == 0:
            score = 2
        elif year_difference <= 1:
            score = 1.5
        elif year_difference <= 2:
            score = 1.2
        elif year_difference <= 4:
            score = 0.7
        elif year_difference <= 6:
            score = 0.3
        elif year_difference <= 8:
            score = 0.1
        else:
            score = 0
        
        if request.user.username != 'david':
            player.player_score = (player.player_score or 0) + score
            if score >= 1:
                player.question_answered = 1
            elif 0 < score < 1:
                player.question_answered = 3
            else:
                player.question_answered = 2

            # Logic to inform the player of their results
            if score > 0:
                messages.success(request, f'You were {year_difference} years off! You have earned {score} points.')
            else:
                messages.error(request, f'You were {year_difference} years off. No points earned.')
        
        # Record the answer and score
        round_name = "Movie Release Dates"
        player.answers.setdefault(round_name, []).append(selected_year)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_year)
            quiz.save()
        
    return iterate_next_question(request)


@login_required
def next_who_is_the_oldest(request):
    if request.method == 'POST':
        selected_order = [item for item in request.POST.getlist('celebrity_order') if item]
        correct_order = request.POST.get('correct_order').split(',')
        
        # Ensure both lists have the same length
        if len(selected_order) != len(correct_order):
            messages.error(request, 'There was an error processing your answer. Please try again.')
            return redirect('active_quiz:active_quiz')
        
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')
        
        # Calculate the score based on the number of correct positions
        correct_positions = sum(1 for i in range(len(selected_order)) if selected_order[i] == correct_order[i])
        if correct_positions == 1:
            score = 0.3
        elif correct_positions == 2:
            score = 0.7
        elif correct_positions == 3:
            score = 1.3
        elif correct_positions == 5:
            score = 2
        else:
            score = 0
        
        if request.user.username != 'david':
            player.player_score = round((player.player_score or 0) + score, 1)
            if score >= 1:
                player.question_answered = 1
            elif 0 < score < 1:
                player.question_answered = 3
            else:
                player.question_answered = 2

            if score > 0:
                messages.success(request, f'You got {correct_positions} correct positions! You have earned {score} points.')
            else:
                messages.error(request, f'You got {correct_positions} correct positions. No points earned.')
        
            # Record the answer and score
            round_name = "Who is the Oldest"
            player.answers.setdefault(round_name, []).append(selected_order)
            player.points.setdefault(round_name, []).append(score)
            player.save()
        
        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_order)
            quiz.save()
        
    return iterate_next_question(request)


@login_required
def next_who_is_the_imposter(request):
    if request.method == 'POST':
        selected_celebrity_id = request.POST.get('selected_celebrity_id')
        imposter_id = request.POST.get('imposter_id')

        if not selected_celebrity_id or not imposter_id:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        selected_celebrity_id = int(selected_celebrity_id)
        imposter_id = int(imposter_id)

        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_celebrity_id == imposter_id:
            player.player_score = (player.player_score or 0) + 1
            player.question_answered = 1  # Correct
            score = 1
            messages.success(request, 'Correct! You have identified the imposter.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            messages.error(request, 'Incorrect. Try again.')

        # Record the answer and score
        round_name = "Who is the Imposter"
        player.answers.setdefault(round_name, []).append(selected_celebrity_id)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(imposter_id)
            quiz.save()

    return iterate_next_question(request)

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
    celebrity_ids = quiz.random_numbers.get("Celebrity Age", [])
    current_celebrity = Celebrities.objects.get(id=celebrity_ids[current_index])
    birth_year = current_celebrity.date_of_birth.year
    current_year = datetime.now().year
    correct_age = current_year - birth_year
    
    # Ensure the correct age is within the range of 18 to 100
    correct_age = max(18, min(correct_age, 100))
    
    # Use a seed to ensure the same answer set for each user
    random.seed(f"{quiz.id}-{current_index}")
    
    # Decide a position for the correct age (e.g., random position within 6 options)
    correct_position = random.randint(0, 5)
    
    # Determine the age interval based on the correct age
    age_interval = 2 if correct_age < 30 else 3
    
    # Generate age options with the specified interval
    age_options = []
    for i in range(6):
        age = correct_age + age_interval * (i - correct_position)
        age = max(18, min(age, 100))  # Ensure age is within the range of 18 to 100
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
    
    return {
        'current_movie': current_movie,
        'correct_year': release_year,
        'current_year': current_year,
    }


def handle_who_is_the_oldest_round(quiz, current_index):
    # Get the list of celebrity ID groups for the "Who is the Oldest" round
    celebrity_id_groups = quiz.random_numbers.get("Who is the Oldest", [])

    # Ensure there are enough celebrity ID groups
    if current_index >= len(celebrity_id_groups):
        raise ValueError(f"Not enough celebrity ID groups to select from")

    # Select the current group of celebrity IDs
    selected_celebrity_ids = celebrity_id_groups[current_index]

    # Fetch the selected celebrities from the database
    celebrities = Celebrities.objects.filter(id__in=selected_celebrity_ids)

    # Sort celebrities by date of birth (oldest first)
    sorted_celebrities = sorted(celebrities, key=lambda c: c.date_of_birth)

    return {
        'celebrities': celebrities,
        'sorted_celebrities': [c.id for c in sorted_celebrities],
    }


def handle_who_is_the_imposter_round(quiz, current_index):
    movie_ids = quiz.random_numbers.get("Who is the Imposter", [])
    current_movie = Movies.objects.get(id=movie_ids[current_index])
    movie_celebrities = list(current_movie.actors.all())

    if len(movie_celebrities) < 4:
        raise ValueError("Not enough celebrities in the movie to create the round")

    # Select 4 celebrities from the movie
    random.seed(f"{quiz.id}-{current_index}")
    selected_celebrities = random.sample(movie_celebrities, 4)

    # Select a random celebrity who is not in the movie
    all_celebrities = list(Celebrities.objects.exclude(id__in=[c.id for c in selected_celebrities]))
    imposter = random.choice(all_celebrities)

    # Combine the selected celebrities and the imposter
    celebrities = selected_celebrities + [imposter]
    random.shuffle(celebrities)

    return {
        'current_movie': current_movie,
        'celebrities': celebrities,
        'imposter': imposter,
    }