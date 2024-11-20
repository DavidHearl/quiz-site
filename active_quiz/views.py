from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, reverse
from quiz_site.models import *

def active_quiz(request):
    quiz = Quiz.objects.latest('date_created')

    # Database assignments
    db_mapping = {
        "General Knowledge": GeneralKnowledge,
        "True or False": TrueOrFalse,
        "Flags": Flags,
        "Capital Cities": Flags,  # Same model as Flags
        "Logos": Logos,
        "Fighter Jets": Jets,
        "Celebrities": Celebrities,
        "Guess the Celebrity Age": Celebrities,
        "Who is the Oldest": Celebrities,
        "Movies": Movies,
        "Who is the Imposter": Movies,
        "Movie Release Dates": Movies,
        "Locations": Locations,
    }

    # Get the list of flag IDs from random_numbers
    flag_ids = quiz.random_numbers.get("Flags", [])
    flags = [Flags.objects.get(id=flag_id) for flag_id in flag_ids]

    # Get the current flag index from the session
    current_flag_index = request.session.get('current_flag_index', 0)

    # Get the current flag
    current_flag = flags[current_flag_index] if flags else None

    context = {
        'quiz': quiz,
        'current_flag': current_flag,
        'current_flag_index': current_flag_index,
        'total_flags': len(flags),
    }

    return render(request, 'active_quiz.html', context)


def next_flag(request):
    # Increment the current flag index
    current_flag_index = request.session.get('current_flag_index', 0)
    current_flag_index += 1
    request.session['current_flag_index'] = current_flag_index

    return redirect('active_quiz')


def previous_flag(request):
    # Decrement the current flag index
    current_flag_index = request.session.get('current_flag_index', 0)
    current_flag_index = max(0, current_flag_index - 1)
    request.session['current_flag_index'] = current_flag_index

    return redirect('active_quiz')