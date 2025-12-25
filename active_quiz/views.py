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
import logging
from django.utils import timezone
import math


logger = logging.getLogger(__name__)

QUESTION_TIMER = 300

# Helper function for fuzzy string matching with partial credit
def calculate_answer_score(user_answer, correct_answer, max_points=1.0):
    """
    Calculate score based on fuzzy string matching.
    Returns a score between 0 and max_points.
    
    Args:
        user_answer: The user's input (string)
        correct_answer: The correct answer (string)
        max_points: Maximum points for a perfect match
    
    Returns:
        tuple: (score, match_type) where match_type is 'exact', 'close', 'partial', or 'incorrect'
    """
    if not user_answer or not correct_answer:
        return 0.0, 'incorrect'
    
    # Normalize strings
    user_normalized = user_answer.lower().strip()
    correct_normalized = correct_answer.lower().strip()
    
    # Remove common articles for better matching
    for article in ['the ', 'a ', 'an ']:
        if user_normalized.startswith(article):
            user_normalized = user_normalized[len(article):]
        if correct_normalized.startswith(article):
            correct_normalized = correct_normalized[len(article):]
    
    # Remove common punctuation
    for char in [':', '-', '.', ',', '!', '?', "'", '"', '(', ')']:
        user_normalized = user_normalized.replace(char, ' ')
        correct_normalized = correct_normalized.replace(char, ' ')
    
    # Normalize whitespace
    user_normalized = ' '.join(user_normalized.split())
    correct_normalized = ' '.join(correct_normalized.split())
    
    # Exact match
    if user_normalized == correct_normalized:
        return max_points, 'exact'
    
    # Calculate Levenshtein distance
    distance = levenshtein_distance(user_normalized, correct_normalized)
    max_length = max(len(user_normalized), len(correct_normalized))
    
    if max_length == 0:
        return 0.0, 'incorrect'
    
    # For very short answers (1-5 chars), allow 1 character difference for full credit
    if max_length <= 5:
        if distance <= 1:
            return max_points, 'close'
        elif distance <= 2:
            return max_points * 0.5, 'partial'
        else:
            return 0.0, 'incorrect'
    
    # For medium answers (6-15 chars), allow 2 character difference for full credit
    elif max_length <= 15:
        if distance <= 2:
            return max_points, 'close'
        elif distance <= 4:
            return max_points * 0.5, 'partial'
        else:
            # Check word overlap for partial credit
            user_words = set(user_normalized.split())
            correct_words = set(correct_normalized.split())
            word_matches = len(user_words & correct_words)
            if word_matches > 0 and len(correct_words) > 0:
                word_score = (word_matches / len(correct_words)) * max_points * 0.3
                return round(word_score, 2), 'partial'
            return 0.0, 'incorrect'
    
    # For longer answers, use ratio-based tolerance
    else:
        tolerance_ratio = distance / max_length
        
        # 90% similarity or better = full credit
        if tolerance_ratio <= 0.1:
            return max_points, 'close'
        # 70-90% similarity = half credit
        elif tolerance_ratio <= 0.3:
            return max_points * 0.5, 'partial'
        # 50-70% similarity = quarter credit
        elif tolerance_ratio <= 0.5:
            return max_points * 0.25, 'partial'
        else:
            # Check word overlap for partial credit
            user_words = set(user_normalized.split())
            correct_words = set(correct_normalized.split())
            word_matches = len(user_words & correct_words)
            if word_matches > 0 and len(correct_words) > 0:
                word_score = (word_matches / len(correct_words)) * max_points * 0.2
                return round(word_score, 2), 'partial'
            return 0.0, 'incorrect'

'''
Main function that controls the active quiz page.
'''

def track_question_for_players(quiz, round_name, question_index):
    """
    Track that all players in the quiz have now seen this question.
    Updates each player's questions_seen field immediately.
    """
    question_ids = quiz.random_numbers.get(round_name, [])
    if not question_ids or question_index >= len(question_ids):
        return
    
    # Get the question ID(s) at this index
    question_id_data = question_ids[question_index]
    
    # Handle nested lists (like "Who is the Oldest" round)
    if isinstance(question_id_data, list):
        question_ids_to_track = question_id_data
    else:
        question_ids_to_track = [question_id_data]
    
    # Update all players in this quiz
    for player_user in quiz.players.all():
        try:
            player = player_user.player
            if not player.questions_seen:
                player.questions_seen = {}
            
            if round_name not in player.questions_seen:
                player.questions_seen[round_name] = []
            
            # Add the question IDs
            for qid in question_ids_to_track:
                if qid not in player.questions_seen[round_name]:
                    player.questions_seen[round_name].append(qid)
            
            player.save()
        except Player.DoesNotExist:
            continue

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
        "General Knowledge": handle_general_knowledge_round,
        "History": handle_history_round,
        "Entertainment": handle_entertainment_round,
        "Maths": handle_maths_round,
        "Pop Culture": handle_pop_culture_round,
        "Mythology": handle_mythology_round,
        "Technology": handle_technology_round,
        "Geography": handle_geography_round,
        "Science": handle_science_round,
        "Sport": handle_sport_round,
        "Flags": handle_flags_round,
        "Capital Cities": handle_capital_cities_round,
        "Celebrities": handle_celebrities_round,
        "Logos": handle_logos_round,
        "True or False": handle_true_or_false_round,
        "Celebrity Age": handle_celebrity_age_round,
        "Movies": handle_movies_round,
        "Movie Release Dates": handle_movie_release_dates_round,
        "Who is the Oldest": handle_who_is_the_oldest_round,
        "Who is the Imposter": handle_who_is_the_imposter_round,
        "Fighter Jets": handle_fighter_jet_round,
        "Music": handle_music_round,
        "Locations": handle_locations_round,
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
        'current_music': None,
        'current_location': None,
    }

    if current_round in round_handlers:
        round_context = round_handlers[current_round](quiz, current_index)
        context.update(round_context)
    
    # Track that all players have now seen this question
    track_question_for_players(quiz, current_round, current_index)

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
    quiz = Quiz.objects.latest('date_created')
    
    player_data = []
    for player in players:
        # Skip adding david to the player data
        if player.user.username != 'david':
            player_data.append({
                'username': player.user.username,
                'score': round(player.player_score, 1),
                'incorrect_answers': player.incorrect_answers,
                'question_answered': player.question_answered,
            })
    
    # Check for countdown condition
    countdown_active = False
    countdown_seconds = 0
    
    # Only check if we're in an active quiz with players
    if quiz:
        # Get players excluding david
        active_players = quiz.players.exclude(username='david')
        total_players = active_players.count()
        
        # Get Player objects for these users
        player_objects = Player.objects.filter(user__in=active_players)
        
        # Count how many have answered (correctly or incorrectly)
        answered_count = player_objects.filter(
            question_answered__in=[1, 2, 3]  # 1=correct, 2=incorrect, 3=partial
        ).count()
        
        # Changed: Only start countdown when all but one player have answered
        if total_players > 1 and answered_count >= total_players - 1:
            # If countdown hasn't started yet, set it now
            if not quiz.countdown_start_time:
                quiz.countdown_start_time = timezone.now()
                quiz.save()
                print("Debug - Starting countdown timer")
            
            # Timer to skip next question
            elapsed = (timezone.now() - quiz.countdown_start_time).total_seconds()
            remaining = max(0, QUESTION_TIMER - math.floor(elapsed))
            
            countdown_active = True
            countdown_seconds = remaining
            
            # If countdown expired, move to next question automatically
            if remaining == 0 and request.user.username == 'david':
                # Reset the countdown timer for next question
                quiz.countdown_start_time = None
                quiz.save()
                
                # Force advancing to next question
                quiz.question_counter += 1
                quiz.save()
                
                # Reset all players' question_answered to 0 (Not Answered)
                for player in Player.objects.all():
                    player.question_answered = 0
                    player.save()
                
                # Tell the frontend to reload the page
                return JsonResponse({
                    'players': player_data,
                    'countdown_active': False,
                    'countdown_seconds': 0,
                    'reload': True
                })
        else:
            # Reset timer if conditions no longer met
            if quiz.countdown_start_time:
                quiz.countdown_start_time = None
                quiz.save()
    
    return JsonResponse({
        'players': player_data,
        'countdown_active': countdown_active,
        'countdown_seconds': countdown_seconds
    })


@login_required
def round_results(request):
    quiz = Quiz.objects.latest('date_created')
    
    # Track questions from the round that just finished
    # This ensures questions are marked as seen even if the quiz doesn't complete
    for player_user in quiz.players.all():
        try:
            player = player_user.player
            if not player.questions_seen:
                player.questions_seen = {}
            
            # Add all question IDs from this quiz to the player's seen questions
            for round_name, question_ids in quiz.random_numbers.items():
                if round_name not in player.questions_seen:
                    player.questions_seen[round_name] = []
                
                # Handle nested lists (like "Who is the Oldest" round)
                if question_ids and isinstance(question_ids[0], list):
                    # Flatten the list
                    flat_ids = [item for sublist in question_ids for item in sublist]
                    for qid in flat_ids:
                        if qid not in player.questions_seen[round_name]:
                            player.questions_seen[round_name].append(qid)
                else:
                    for qid in question_ids:
                        if qid not in player.questions_seen[round_name]:
                            player.questions_seen[round_name].append(qid)
            
            player.save()
        except Player.DoesNotExist:
            continue
    
    # Fix player selection logic
    if request.user.username == 'david':
        # Quiz master sees all players except themselves
        players = quiz.players.exclude(username='david')
    else:
        # Regular player only sees their own results
        players = User.objects.filter(id=request.user.id)
    
    # Determine the current round based on question_counter (same logic as active_quiz)
    question_counter = quiz.question_counter
    rounds = quiz.rounds.all()
    current_round = None
    temp_counter = question_counter
    
    # Find which round we just finished by checking question_counter
    for round in rounds:
        round_name = round.question_type
        total_questions = len(quiz.random_numbers.get(round_name, []))
        if temp_counter <= total_questions:
            current_round = round_name
            break
        temp_counter -= total_questions
    
    # If we didn't find a round, use the last round in correct_answers as fallback
    if current_round is None and quiz.correct_answers:
        current_round = list(quiz.correct_answers.keys())[-1]

    total_questions = len(rounds) * 10

    # Determine the start and end indices for the last 10 questions
    start_index = max(0, question_counter - 10)
    end_index = question_counter

    correct_answers = quiz.correct_answers.get(current_round, []) if current_round else []
    last_10_answers = correct_answers[-10:] if correct_answers else []

    # Combine answers and points for the current round
    combined_player_data = {}
    if current_round:
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
    
    # Track questions seen by all players in this quiz
    for player_user in quiz.players.all():
        try:
            player = player_user.player
            if not player.questions_seen:
                player.questions_seen = {}
            
            # Add all question IDs from this quiz to the player's seen questions
            for round_name, question_ids in quiz.random_numbers.items():
                if round_name not in player.questions_seen:
                    player.questions_seen[round_name] = []
                
                # Handle nested lists (like "Who is the Oldest" round)
                if question_ids and isinstance(question_ids[0], list):
                    # Flatten the list
                    flat_ids = [item for sublist in question_ids for item in sublist]
                    player.questions_seen[round_name].extend(flat_ids)
                else:
                    player.questions_seen[round_name].extend(question_ids)
                
                # Remove duplicates
                player.questions_seen[round_name] = list(set(player.questions_seen[round_name]))
            
            player.save()
        except Player.DoesNotExist:
            # Skip if player doesn't have a Player profile
            continue
    
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
            player.player_score = round((player.player_score or 0) + 1, 1)
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

        # Adjust question difficulty based on answer correctness
        is_correct = selected_answer == correct_answer
        adjust_question_difficulty(quiz, round_name, is_correct)

    return iterate_next_question(request)


@login_required
def next_general_knowledge(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        # Determine if answer is correct
        is_correct = selected_answer == correct_answer

        if is_correct:
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 2
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

        # Adjust question difficulty based on answer correctness
        adjust_question_difficulty(quiz, round_name, is_correct)

    return iterate_next_question(request)


@login_required
def next_fighter_jet(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        question_type = request.POST.get('question_type')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        logger.debug(f"Selected answer: {selected_answer}")
        logger.debug(f"Correct answer: {correct_answer}")
        logger.debug(f"Question type: {question_type}")
        print('Statment Called')

        if selected_answer == correct_answer:
            player.player_score = round((player.player_score or 0) + 1.5, 1)
            player.question_answered = 1  # Correct
            score = 1.5
            messages.success(request, 'Correct answer! You have earned 1.5 points.')
            logger.debug(f"Player {player.user.username} answered correctly. Score: {score}")
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')
            logger.debug(f"Player {player.user.username} answered incorrectly. Score: {score}")

        round_name = "Fighter Jets"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        logger.debug(f"Player answers: {player.answers}")
        logger.debug(f"Player points: {player.points}")

        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()
            logger.debug(f"Correct answer saved to quiz: {correct_answer}")

        # Adjust question difficulty based on answer correctness
        is_correct = selected_answer == correct_answer
        adjust_question_difficulty(quiz, round_name, is_correct)

    return iterate_next_question(request)


@login_required
def next_music(request):
    if request.method == 'POST':
        artist_answer = request.POST.get('artist_answer', '').strip()
        song_answer = request.POST.get('song_answer', '').strip()
        correct_artist = request.POST.get('correct_artist', '')
        correct_song = request.POST.get('correct_song', '')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        # Use the fuzzy matching helper for both artist and song
        artist_score, artist_match_type = calculate_answer_score(artist_answer, correct_artist, max_points=1.0)
        song_score, song_match_type = calculate_answer_score(song_answer, correct_song, max_points=1.0)
        
        # Total score (max 2 points: 1 for artist + 1 for song)
        total_score = round(artist_score + song_score, 2)
        
        # Update player stats
        player.player_score = round((player.player_score or 0) + total_score, 1)
        
        # Provide feedback based on score
        if total_score >= 2.0:
            player.question_answered = 1  # Fully Correct
            messages.success(request, f'Perfect! You earned {total_score:.1f} points!')
        elif total_score >= 1.5:
            player.question_answered = 1  # Mostly Correct
            messages.success(request, f'Great! You earned {total_score:.1f} points!')
        elif total_score >= 1.0:
            player.question_answered = 3  # Partial
            feedback_parts = []
            if artist_score >= 0.5:
                feedback_parts.append("artist")
            if song_score >= 0.5:
                feedback_parts.append("song")
            feedback = f"Good! You got the {' and '.join(feedback_parts)}. You earned {total_score:.1f} points."
            messages.warning(request, feedback)
        elif total_score > 0:
            player.question_answered = 3  # Partial
            messages.warning(request, f'Partial credit. You earned {total_score:.1f} points.')
        else:
            player.question_answered = 2  # Incorrect
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            if request.user.username != 'david':
                messages.error(request, f'Incorrect. The answer was "{correct_artist} - {correct_song}". No points earned.')

        # Record the answer and score
        round_name = "Music"
        combined_answer = f"{artist_answer} - {song_answer}"
        player.answers.setdefault(round_name, []).append(combined_answer)
        player.points.setdefault(round_name, []).append(total_score)
        player.save()

        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            correct_answer = f"{correct_artist} - {correct_song}"
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

        # Adjust question difficulty based on answer correctness (consider partial credit as correct)
        is_correct = total_score > 0
        adjust_question_difficulty(quiz, round_name, is_correct)

    return iterate_next_question(request)


@login_required
def next_history(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 1.5
            messages.success(request, 'Correct answer! You have earned 1.5 point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        # Record the answer and score
        round_name = "History"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

        # Adjust question difficulty based on answer correctness
        is_correct = selected_answer == correct_answer
        adjust_question_difficulty(quiz, round_name, is_correct)

    return iterate_next_question(request)


@login_required
def next_entertainment(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 1.5
            messages.success(request, 'Correct answer! You have earned 1.5 points.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        round_name = "Entertainment"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

        # Adjust question difficulty based on answer correctness
        is_correct = selected_answer == correct_answer
        adjust_question_difficulty(quiz, round_name, is_correct)

    return iterate_next_question(request)


@login_required
def next_maths(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 1.5
            messages.success(request, 'Correct answer! You have earned 1.5 points.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        round_name = "Maths"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

    return iterate_next_question(request)


@login_required
def next_pop_culture(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 2
            messages.success(request, 'Correct answer! You have earned 1 point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        round_name = "Pop Culture"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

    return iterate_next_question(request)


@login_required
def next_mythology(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 2
            messages.success(request, 'Correct answer! You have earned 1 point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        round_name = "Mythology"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

    return iterate_next_question(request)


@login_required
def next_technology(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 2
            messages.success(request, 'Correct answer! You have earned 1 point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        round_name = "Technology"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

        # Adjust question difficulty based on answer correctness
        is_correct = selected_answer == correct_answer
        adjust_question_difficulty(quiz, round_name, is_correct)

    return iterate_next_question(request)


@login_required
def next_geography(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 2
            messages.success(request, 'Correct answer! You have earned 1 point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        round_name = "Geography"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

    return iterate_next_question(request)


@login_required
def next_science(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 2
            messages.success(request, 'Correct answer! You have earned 1 point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        round_name = "Science"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_answer)
            quiz.save()

    return iterate_next_question(request)


@login_required
def next_sport(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        if selected_answer == correct_answer:
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 2
            messages.success(request, 'Correct answer! You have earned 1 point.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, 'Incorrect answer. No points earned.')

        round_name = "Mythology"
        player.answers.setdefault(round_name, []).append(selected_answer)
        player.points.setdefault(round_name, []).append(score)
        player.save()

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
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 1.3
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


@login_required
def next_celebrity(request):
    if request.method == 'POST':
        selected_first_name = request.POST.get('first_name', '').strip()
        selected_last_name = request.POST.get('last_name', '').strip()
        correct_first_name = request.POST.get('correct_first_name', '').strip()
        correct_last_name = request.POST.get('correct_last_name', '').strip()
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')

        # Use fuzzy matching helper for both first and last names
        first_name_score, first_match_type = calculate_answer_score(selected_first_name, correct_first_name, max_points=0.5)
        last_name_score, last_match_type = calculate_answer_score(selected_last_name, correct_last_name, max_points=0.5)
        
        total_score = round(first_name_score + last_name_score, 2)
        
        # Determine question status and award points
        if total_score >= 1.0:
            player.player_score = round((player.player_score or 0) + 1, 1)
            player.question_answered = 1  # Correct
            score = 1
            messages.success(request, f'Correct! You have earned 1 point.')
        elif total_score >= 0.5:
            player.player_score = round((player.player_score or 0) + 0.5, 1)
            player.question_answered = 3  # Partially correct
            score = 0.5
            if first_name_score > last_name_score:
                messages.warning(request, f'Partially correct! You got the first name. You earned 0.5 points.')
            else:
                messages.warning(request, f'Partially correct! You got the last name. You earned 0.5 points.')
        elif total_score > 0:
            player.player_score = round((player.player_score or 0) + 0.25, 1)
            player.question_answered = 3  # Partially correct
            score = 0.25
            messages.warning(request, f'Close! You earned {score} points.')
        else:
            player.incorrect_answers = (player.incorrect_answers or 0) + 1
            player.question_answered = 2  # Incorrect
            score = 0
            if request.user.username != 'david':
                messages.error(request, f'Incorrect. The answer was "{correct_first_name} {correct_last_name}".')

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
        
        # Use fuzzy matching helper
        score, match_type = calculate_answer_score(selected_answer, correct_answer, max_points=1.0)
        
        if request.user.username != 'david':
            if score >= 1.0:
                player.player_score = round((player.player_score or 0) + 1, 1)
                player.question_answered = 1  # Correct
                messages.success(request, f'Correct! You earned 1 point.')
            elif score > 0:
                player.player_score = round((player.player_score or 0) + score, 1)
                player.question_answered = 3  # Partial
                messages.warning(request, f'Close! You earned {score:.1f} points.')
            else:
                player.incorrect_answers = (player.incorrect_answers or 0) + 1
                player.question_answered = 2  # Incorrect
                messages.error(request, f'Incorrect. The answer was "{correct_answer}". No points earned.')
        
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
def next_location(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('location', '').strip()
        correct_answer = request.POST.get('correct_location', '')
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')
        
        # Use fuzzy matching helper
        score, match_type = calculate_answer_score(selected_answer, correct_answer, max_points=1.0)
        
        if request.user.username != 'david':
            if score >= 1.0:
                player.player_score = round((player.player_score or 0) + 1, 1)
                player.question_answered = 1  # Correct
                messages.success(request, f'Correct! You earned 1 point.')
            elif score >= 0.5:
                player.player_score = round((player.player_score or 0) + score, 1)
                player.question_answered = 3  # Partial
                messages.warning(request, f'Close! You earned {score:.1f} points.')
            elif score > 0:
                player.player_score = round((player.player_score or 0) + score, 1)
                player.question_answered = 3  # Partial
                messages.info(request, f'Partial credit. You earned {score:.1f} points.')
            else:
                player.incorrect_answers = (player.incorrect_answers or 0) + 1
                player.question_answered = 2  # Incorrect
                messages.error(request, f'Incorrect. The answer was "{correct_answer}". No points earned.')
        
        # Record the answer and score
        round_name = "Locations"
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
                player.player_score = round((player.player_score or 0) + 1, 1)
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

        # Adjust question difficulty based on answer correctness
        is_correct = selected_answer == correct_answer
        adjust_question_difficulty(quiz, round_name, is_correct)

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
        elif age_difference <=3:
            score = 1
        elif age_difference <= 4:
            score = 0.7
        elif age_difference <= 6:
            score = 0.3
        elif age_difference <= 8:
            score = 0.1
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
        
        player = request.user.player
        round_name = "Movie Release Dates"
        
        # Quiz master can skip without selecting
        if request.user.username == 'david':
            # Just move to next question
            pass
        else:
            # Players must provide a year
            if selected_year is None or correct_year is None:
                messages.error(request, 'Both the selected and correct years must be provided.')
                return redirect('active_quiz:active_quiz')
            
            selected_year = int(selected_year)
            correct_year = int(correct_year)
            
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
            
            player.player_score = round((player.player_score or 0) + score, 1)
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
            player.answers.setdefault(round_name, []).append(selected_year)
            player.points.setdefault(round_name, []).append(round(score, 1))
            player.save()

            # Save the correct answer to quiz.correct_answers if not already saved
            if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
                quiz.correct_answers.setdefault(round_name, []).append(correct_year)
                quiz.save()
        
    return iterate_next_question(request)


@login_required
def next_movie(request):
    if request.method == 'POST':
        quiz = Quiz.objects.latest('date_created')
        movie_title = request.POST.get('movie_title', '').strip()
        correct_title = request.POST.get('correct_title', '').strip()
        
        if request.user.username != 'david' and not movie_title:
            messages.error(request, 'Please enter a movie title.')
            return redirect('active_quiz:active_quiz')
        
        player = request.user.player
        
        if request.user.username != 'david':
            # Use fuzzy matching helper
            score, match_type = calculate_answer_score(movie_title, correct_title, max_points=1.0)
            
            # Award feedback based on score
            if score >= 1.0:
                messages.success(request, f'Correct! You earned {score:.1f} points.')
                player.question_answered = 1
            elif score >= 0.5:
                messages.success(request, f'Close enough! You earned {score:.1f} points.')
                player.question_answered = 1
            elif score > 0:
                messages.info(request, f'Almost! The correct answer was "{correct_title}". You earned {score:.1f} points.')
                player.question_answered = 3
            else:
                messages.error(request, f'Incorrect. The correct answer was "{correct_title}". No points earned.')
                player.question_answered = 2
            
            player.player_score = round((player.player_score or 0) + score, 1)
        else:
            score = 0
        
        # Record the answer and score
        round_name = "Movies"
        player.answers.setdefault(round_name, []).append(movie_title if movie_title else correct_title)
        player.points.setdefault(round_name, []).append(round(score, 1))
        player.save()

        # Save the correct answer to quiz.correct_answers if not already saved
        if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
            quiz.correct_answers.setdefault(round_name, []).append(correct_title)
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
        round_name = "Who is the Oldest"  # Define round_name here
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
        
        player = request.user.player
        quiz = Quiz.objects.latest('date_created')
        round_name = "Who is the Imposter"

        # Quiz master can skip without selecting
        if request.user.username == 'david':
            # Just move to next question
            pass
        else:
            # Players must select an answer
            if not selected_celebrity_id or not imposter_id:
                messages.error(request, 'Please select a celebrity.')
                return redirect('active_quiz:active_quiz')
            
            selected_celebrity_id = int(selected_celebrity_id)
            imposter_id = int(imposter_id)
            
            if selected_celebrity_id == imposter_id:
                score = 1.5
                player.player_score = round((player.player_score or 0) + score, 1)
                player.question_answered = 1  # Correct
                messages.success(request, f'Correct! You earned {score} points.')
            else:
                score = 0
                player.question_answered = 2  # Incorrect
                messages.error(request, 'Incorrect. No points earned.')

            # Record the answer and score
            player.answers.setdefault(round_name, []).append(selected_celebrity_id)
            player.points.setdefault(round_name, []).append(score)
            player.save()

            # Save the correct answer to quiz.correct_answers if not already saved
            if len(player.answers[round_name]) > len(quiz.correct_answers.get(round_name, [])):
                quiz.correct_answers.setdefault(round_name, []).append(imposter_id)
                quiz.save()

    return iterate_next_question(request)

def adjust_question_difficulty(quiz, round_name, is_correct):
    """Adjust the difficulty of a question based on whether it was answered correctly."""
    try:
        # Get the question that was just answered
        question_ids = quiz.random_numbers.get(round_name, [])
        rounds = quiz.rounds.all()
        question_counter = quiz.question_counter
        current_index = 0

        # Calculate which question index was just answered
        for round_obj in rounds:
            round_questions = len(quiz.random_numbers.get(round_obj.question_type, []))
            if question_counter < round_questions:
                if round_obj.question_type == round_name:
                    current_index = question_counter
                break
            question_counter -= round_questions

        if current_index < len(question_ids):
            question_id = question_ids[current_index]

            # Adjust difficulty based on question type
            if round_name in ["General Knowledge", "History", "Entertainment", "Maths", "Pop Culture", "Mythology", "Technology", "Geography", "Science", "Sport"]:
                # These use GeneralKnowledge model with different categories
                category_name = round_name if round_name != "General Knowledge" else "General"
                category = GeneralKnowledgeCategory.objects.get(category=category_name)
                question = GeneralKnowledge.objects.get(id=question_id, category=category)
            elif round_name == "Flags":
                question = Flags.objects.get(id=question_id)
            elif round_name == "True or False":
                question = TrueOrFalse.objects.get(id=question_id)
            elif round_name == "Fighter Jets":
                question = Jets.objects.get(id=question_id)
            elif round_name == "Celebrities":
                question = Celebrities.objects.get(id=question_id)
            elif round_name == "Movies":
                question = Movies.objects.get(id=question_id)
            elif round_name == "Locations":
                question = Locations.objects.get(id=question_id)
            elif round_name == "Music":
                question = Music.objects.get(id=question_id)
            else:
                return  # Unknown question type

            # Adjust difficulty
            if is_correct:
                question.difficulty = (question.difficulty or 0.5) * 0.99
            else:
                question.difficulty = (question.difficulty or 0.5) * 1.01

            question.save()

    except (GeneralKnowledgeCategory.DoesNotExist, GeneralKnowledge.DoesNotExist, Flags.DoesNotExist,
            TrueOrFalse.DoesNotExist, Jets.DoesNotExist, Celebrities.DoesNotExist,
            Movies.DoesNotExist, Locations.DoesNotExist, Music.DoesNotExist,
            IndexError, KeyError):
        # If we can't find the question or category, just continue without adjusting difficulty
        pass

def handle_general_knowledge_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("General Knowledge", [])
    general_category = GeneralKnowledgeCategory.objects.get(category='General')
    
    # Get specific question by ID from random_numbers array at current_index
    current_question_id = question_ids[current_index]
    current_question = GeneralKnowledge.objects.get(
        id=current_question_id,
        category=general_category
    )
    
    gk_choices = [current_question.answer, current_question.choice_1, 
                 current_question.choice_2, current_question.choice_3]
    random.shuffle(gk_choices)

    return {
        'current_question': current_question,
        'gk_choices': gk_choices,
    }


def handle_history_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("History", [])
    history_category = GeneralKnowledgeCategory.objects.get(category='History')
    
    # Get specific question by ID from random_numbers array at current_index
    current_question_id = question_ids[current_index]
    current_question = GeneralKnowledge.objects.get(
        id=current_question_id,
        category=history_category
    )
    
    history_choices = [current_question.answer, current_question.choice_1, 
                      current_question.choice_2, current_question.choice_3]
    random.shuffle(history_choices)

    return {
        'current_question': current_question,
        'gk_choices': history_choices,  # Keep same key name for template compatibility
    }


def handle_entertainment_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("Entertainment", [])
    category = GeneralKnowledgeCategory.objects.get(category='Entertainment')
    current_question_id = question_ids[current_index]
    current_question = GeneralKnowledge.objects.get(id=current_question_id, category=category)
    choices = [current_question.answer, current_question.choice_1, 
              current_question.choice_2, current_question.choice_3]
    random.shuffle(choices)
    return {
        'current_question': current_question,
        'gk_choices': choices,
    }


def handle_maths_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("Maths", [])
    category = GeneralKnowledgeCategory.objects.get(category='Maths')
    current_question_id = question_ids[current_index]

    # Log the values of current_question_id and category
    logger.debug(f"Maths Round - current_question_id: {current_question_id}, category: {category}")

    try:
        current_question = GeneralKnowledge.objects.get(id=current_question_id, category=category)
    except GeneralKnowledge.DoesNotExist:
        logger.error(f"GeneralKnowledge with id {current_question_id} and category {category} does not exist.")
        raise

    choices = [current_question.answer, current_question.choice_1, 
              current_question.choice_2, current_question.choice_3]
    random.shuffle(choices)
    return {
        'current_question': current_question,
        'gk_choices': choices,
    }


def handle_pop_culture_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("Pop Culture", [])
    category = GeneralKnowledgeCategory.objects.get(category='Pop Culture')
    current_question_id = question_ids[current_index]
    current_question = GeneralKnowledge.objects.get(id=current_question_id, category=category)
    choices = [current_question.answer, current_question.choice_1, 
              current_question.choice_2, current_question.choice_3]
    random.shuffle(choices)
    return {
        'current_question': current_question,
        'gk_choices': choices,
    }


def handle_mythology_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("Mythology", [])
    category = GeneralKnowledgeCategory.objects.get(category='Mythology')
    current_question_id = question_ids[current_index]
    current_question = GeneralKnowledge.objects.get(id=current_question_id, category=category)
    choices = [current_question.answer, current_question.choice_1, 
              current_question.choice_2, current_question.choice_3]
    random.shuffle(choices)
    return {
        'current_question': current_question,
        'gk_choices': choices,
    }


def handle_technology_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("Technology", [])
    category = GeneralKnowledgeCategory.objects.get(category='Technology')
    current_question_id = question_ids[current_index]
    current_question = GeneralKnowledge.objects.get(id=current_question_id, category=category)
    choices = [current_question.answer, current_question.choice_1, 
              current_question.choice_2, current_question.choice_3]
    random.shuffle(choices)
    return {
        'current_question': current_question,
        'gk_choices': choices,
    }


def handle_geography_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("Geography", [])
    category = GeneralKnowledgeCategory.objects.get(category='Geography')
    current_question_id = question_ids[current_index]
    current_question = GeneralKnowledge.objects.get(id=current_question_id, category=category)
    choices = [current_question.answer, current_question.choice_1, 
              current_question.choice_2, current_question.choice_3]
    random.shuffle(choices)
    return {
        'current_question': current_question,
        'gk_choices': choices,
    }


def handle_science_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("Science", [])
    category = GeneralKnowledgeCategory.objects.get(category='Science')
    current_question_id = question_ids[current_index]
    current_question = GeneralKnowledge.objects.get(id=current_question_id, category=category)
    choices = [current_question.answer, current_question.choice_1, 
              current_question.choice_2, current_question.choice_3]
    random.shuffle(choices)
    return {
        'current_question': current_question,
        'gk_choices': choices,
    }


def handle_sport_round(quiz, current_index):
    question_ids = quiz.random_numbers.get("Sport", [])
    category = GeneralKnowledgeCategory.objects.get(category='Sport')
    current_question_id = question_ids[current_index]
    current_question = GeneralKnowledge.objects.get(id=current_question_id, category=category)
    choices = [current_question.answer, current_question.choice_1, 
              current_question.choice_2, current_question.choice_3]
    random.shuffle(choices)
    return {
        'current_question': current_question,
        'gk_choices': choices,
    }


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


def handle_movies_round(quiz, current_index):
    movie_ids = quiz.random_numbers.get("Movies", [])
    current_movie = Movies.objects.get(id=movie_ids[current_index])
    
    # Get 4 actors from the movie
    actors = list(current_movie.actors.all())[:4]
    
    return {
        'current_movie': current_movie,
        'actors': actors,
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


def handle_fighter_jet_round(quiz, current_index):
    jet_ids = quiz.random_numbers.get("Fighter Jets", [])
    current_jet = Jets.objects.get(id=jet_ids[current_index])
    random.seed(f"{quiz.id}-{current_index}")

    # Determine if the question will be based on name or code_name
    question_type = 'name' if current_index % 2 == 1 else 'code_name'
    if question_type == 'name':
        correct_answer = current_jet.name
        all_options = Jets.objects.exclude(id=current_jet.id).values_list('name', flat=True)
    else:
        correct_answer = current_jet.code_name
        all_options = Jets.objects.exclude(id=current_jet.id).values_list('code_name', flat=True)

    choices = random.sample(list(all_options), 3) + [correct_answer]
    random.shuffle(choices)

    return {
        'current_jet': current_jet,
        'choices': choices,
        'question_type': question_type,
        'correct_answer': correct_answer,
    }


def handle_music_round(quiz, current_index):
    music_ids = quiz.random_numbers.get("Music", [])
    current_music = Music.objects.get(id=music_ids[current_index])
    
    return {
        'current_music': current_music,
    }


def handle_locations_round(quiz, current_index):
    location_ids = quiz.random_numbers.get("Locations", [])
    current_location = Locations.objects.get(id=location_ids[current_index])
    obfuscated_name = ''.join('*' if char != ' ' else ' ' for char in current_location.location)
    
    return {
        'current_location': current_location,
        'obfuscated_name': obfuscated_name,
    }