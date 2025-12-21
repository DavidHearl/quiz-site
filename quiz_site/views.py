from django.db.models import Count
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, reverse
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import *
from .forms import *
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import random
from django.core.serializers.json import DjangoJSONEncoder
import json


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the user
            user = form.save()
            
            # Create or update the player profile
            player, created = Player.objects.get_or_create(user=user)
            
            # Save the photo if provided
            if 'player_photo' in request.FILES:
                player.player_photo = request.FILES['player_photo']
                player.save()
                
            # Log the user in
            login(request, user)
            
            # Redirect to home page
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

'''
Home, the user can select to be a quiz master or a player and enter a code
'''
def home(request):
    if request.method == 'POST':
        # Handle participant joining with code
        if 'join_code' in request.POST:
            join_code = request.POST.get('join_code')
            if join_code:
                try:
                    quiz = Quiz.objects.get(join_code=join_code)
                    # Add the current user to the quiz if they're not already in it
                    if request.user.is_authenticated and request.user not in quiz.players.all():
                        quiz.players.add(request.user)
                        quiz.save()
                    return redirect('loading_page') 
                except Quiz.DoesNotExist:
                    messages.error(request, 'Invalid join code. Please try again.')
        
        # Handle simple quiz creation
        elif 'quiz_name' in request.POST:
            quiz_name = request.POST.get('quiz_name')
            if quiz_name:
                quiz = Quiz.objects.create(quiz_name=quiz_name)
                
                # Generate a random 4-character join code
                def generate_join_code():
                    import string
                    import random
                    chars = string.ascii_uppercase + string.digits
                    code = ''.join(random.choice(chars) for _ in range(4))
                    # Check if code already exists
                    if Quiz.objects.filter(join_code=code).exists():
                        return generate_join_code()  # Try again if exists
                    return code
                
                # Set the join code
                quiz.join_code = generate_join_code()
                
                # If user is authenticated, add them as a player
                if request.user.is_authenticated:
                    quiz.players.add(request.user)
                
                quiz.save()
                
                messages.success(request, f'Quiz created! Join code: {quiz.join_code}')
                return redirect('quiz_home')  # Redirect to select rounds, etc.
    
    return render(request, 'quiz_site/home.html')


@login_required
def manage_quizzes(request):
    """
    View to manage all quizzes - list, view details, and delete
    """
    # Get all quizzes ordered by most recent first
    quizzes = Quiz.objects.all().order_by('-date_created')
    
    if request.method == 'POST':
        if 'delete_quiz' in request.POST:
            quiz_id = request.POST.get('delete_quiz')
            try:
                quiz = Quiz.objects.get(id=quiz_id)
                quiz_name = quiz.quiz_name
                quiz.delete()
                messages.success(request, f'Quiz "{quiz_name}" has been deleted.')
            except Quiz.DoesNotExist:
                messages.error(request, 'Quiz not found.')
            return redirect('manage_quizzes')
    
    context = {
        'quizzes': quizzes,
    }
    
    return render(request, 'quiz_site/manage_quizzes.html', context)


'''
This view is used to create the quiz. The user can select the players, rounds and the quiz name.
The question sets are created for the active quiz.
'''
def quiz_home(request):
    users = User.objects.all()
    rounds = Rounds.objects.all()

    # Get the most recently created quiz
    latest_quiz = Quiz.objects.order_by('-date_created').first()
    
    current_players = []
    if latest_quiz:
        current_players = latest_quiz.players.exclude(username='david')

    db_mapping = {
        "General Knowledge": GeneralKnowledge,
        "History": GeneralKnowledge,
        "Entertainment": GeneralKnowledge,
        "Maths": GeneralKnowledge, 
        "Pop Culture": GeneralKnowledge,
        "Mythology": GeneralKnowledge,
        "Technology": GeneralKnowledge,
        "Geography": GeneralKnowledge,
        "Science": GeneralKnowledge,
        "Sport": GeneralKnowledge,
        "True or False": TrueOrFalse,
        "Flags": Flags,
        "Capital Cities": Flags,
        "Logos": Logos,
        "Fighter Jets": Jets,
        "Celebrities": Celebrities,
        "Celebrity Age": Celebrities,
        "Who is the Oldest": Celebrities,
        "Movies": Movies,
        "Movie Release Dates": Movies,
        "Who is the Imposter": Movies,
        "Music": Music,
        "Locations": Locations,
    }

    # Initialize dictionary to store previously seen questions by round
    previously_seen_questions = {round_name: set() for round_name in db_mapping.keys()}
    
    # Get all quizzes that current players have participated in
    if current_players:
        player_quizzes = Quiz.objects.filter(players__in=current_players).distinct()
        
        # Extract previously seen question IDs for each round
        for quiz in player_quizzes:
            if not quiz.random_numbers:
                continue
                
            for round_name, question_ids in quiz.random_numbers.items():
                if round_name not in previously_seen_questions:
                    continue
                    
                # Handle different structures of question_ids
                if isinstance(question_ids, list):
                    if any(isinstance(x, list) for x in question_ids):
                        # Handle nested lists (like for "Who is the Oldest")
                        flattened = [item for sublist in question_ids for item in 
                                     (sublist if isinstance(sublist, list) else [sublist])]
                        previously_seen_questions[round_name].update(flattened)
                    else:
                        previously_seen_questions[round_name].update(question_ids)
                else:
                    previously_seen_questions[round_name].add(question_ids)

    # Count available questions for each round
    question_counts = {}
    for round_name, model in db_mapping.items():
        base_query = model.objects.all()
        
        # Apply category filters for GeneralKnowledge-based rounds
        if round_name == "General Knowledge":
            try:
                category = GeneralKnowledgeCategory.objects.get(category='General')
                base_query = base_query.filter(category=category)
            except GeneralKnowledgeCategory.DoesNotExist:
                base_query = model.objects.none()
        elif round_name == "History":
            try:
                category = GeneralKnowledgeCategory.objects.get(category='History')
                base_query = base_query.filter(category=category)
            except GeneralKnowledgeCategory.DoesNotExist:
                base_query = model.objects.none()
        elif round_name == "Entertainment" or round_name == "Pop Culture":
            try:
                # Query both Entertainment and Pop Culture categories
                entertainment_cat = GeneralKnowledgeCategory.objects.get(category='Entertainment')
                pop_culture_cat = GeneralKnowledgeCategory.objects.get(category='Pop Culture')
                base_query = base_query.filter(category__in=[entertainment_cat, pop_culture_cat])
            except GeneralKnowledgeCategory.DoesNotExist:
                base_query = model.objects.none()
        elif round_name == "Maths":
            try:
                category = GeneralKnowledgeCategory.objects.get(category='Maths')
                base_query = base_query.filter(category=category)
            except GeneralKnowledgeCategory.DoesNotExist:
                base_query = model.objects.none()
        elif round_name == "Mythology":
            try:
                category = GeneralKnowledgeCategory.objects.get(category='Mythology')
                base_query = base_query.filter(category=category)
            except GeneralKnowledgeCategory.DoesNotExist:
                base_query = model.objects.none()
        elif round_name == "Technology":
            try:
                category = GeneralKnowledgeCategory.objects.get(category='Technology')
                base_query = base_query.filter(category=category)
            except GeneralKnowledgeCategory.DoesNotExist:
                base_query = model.objects.none()
        elif round_name == "Geography":
            try:
                category = GeneralKnowledgeCategory.objects.get(category='Geography')
                base_query = base_query.filter(category=category)
            except GeneralKnowledgeCategory.DoesNotExist:
                base_query = model.objects.none()
        elif round_name == "Science":
            try:
                category = GeneralKnowledgeCategory.objects.get(category='Science')
                base_query = base_query.filter(category=category)
            except GeneralKnowledgeCategory.DoesNotExist:
                base_query = model.objects.none()
        elif round_name == "Sport":
            try:
                category = GeneralKnowledgeCategory.objects.get(category='Sport')
                base_query = base_query.filter(category=category)
            except GeneralKnowledgeCategory.DoesNotExist:
                base_query = model.objects.none()
        elif round_name == "Capital Cities":
            base_query = base_query.filter(capital__isnull=False).exclude(capital='')
        elif round_name == "Movies":
            # Filter movies that have at least 4 actors
            base_query = Movies.objects.annotate(actor_count=Count('actors')).filter(actor_count__gte=4)
        elif round_name == "Movie Release Dates":
            base_query = Movies.objects.filter(release_date__isnull=False)
        elif round_name == "Who is the Imposter":
            # Filter movies that have at least 4 actors (need 4 from movie + 1 imposter)
            base_query = Movies.objects.annotate(actor_count=Count('actors')).filter(actor_count__gte=4)
            
        # Exclude questions previously seen by current players
        if previously_seen_questions[round_name]:
            base_query = base_query.exclude(id__in=previously_seen_questions[round_name])
        
        # Count questions in special way for "Who is the Oldest"
        if round_name == "Who is the Oldest":
            total_celebrities = base_query.count()
            # We need sets of 5, so divide by 5 and round down
            count = total_celebrities // 5
        else:
            count = base_query.count()
            
        question_counts[round_name] = count

    if request.method == 'POST':
        quiz_selection_form = QuizSelectionForm(request.POST)
        if quiz_selection_form.is_valid():
            # Use the existing quiz instead of creating a new one
            # This preserves the join code so players don't need a new one
            quiz = latest_quiz
            
            # Reset player-specific data 
            for player in Player.objects.all():
                player.player_score = 0
                player.incorrect_answers = 0
                player.question_answered = 0
                player.page_updates = 0
                player.answers = {}
                player.points = {}
                player.save()
            
            # Only update the rounds, not the players
            selected_rounds = quiz_selection_form.cleaned_data['rounds']
            quiz.rounds.set(selected_rounds)
            random_numbers = {}
            exclude_previous = quiz_selection_form.cleaned_data.get('exclude_previous', False)

            for round in selected_rounds:
                round_name = round.question_type
                if round_name in db_mapping:
                    model = db_mapping[round_name]
                    base_query = model.objects.all()

                    # Apply category filters first
                    if round_name == "General Knowledge":
                        general_category = GeneralKnowledgeCategory.objects.get(category='General')
                        base_query = base_query.filter(category=general_category)
                    elif round_name == "Maths":
                        category = GeneralKnowledgeCategory.objects.get(category='Maths')
                        base_query = base_query.filter(category=category)
                    elif round_name == "Pop Culture":
                        category = GeneralKnowledgeCategory.objects.get(category='Pop Culture')
                        base_query = base_query.filter(category=category)
                    elif round_name == "History":
                        history_category = GeneralKnowledgeCategory.objects.get(category='History')
                        base_query = base_query.filter(category=history_category)
                    elif round_name == "Entertainment" or round_name == "Pop Culture":
                        entertainment_category = GeneralKnowledgeCategory.objects.get(category='Entertainment')
                        pop_culture_category = GeneralKnowledgeCategory.objects.get(category='Pop Culture')
                        base_query = base_query.filter(category__in=[entertainment_category, pop_culture_category])
                    elif round_name == "Mythology":
                        category = GeneralKnowledgeCategory.objects.get(category='Mythology')
                        base_query = base_query.filter(category=category)
                    elif round_name == "Technology":
                        category = GeneralKnowledgeCategory.objects.get(category='Technology')
                        base_query = base_query.filter(category=category)
                    elif round_name == "Geography":
                        category = GeneralKnowledgeCategory.objects.get(category='Geography')
                        base_query = base_query.filter(category=category)
                    elif round_name == "Science":
                        category = GeneralKnowledgeCategory.objects.get(category='Science')
                        base_query = base_query.filter(category=category)
                    elif round_name == "Sport":
                        category = GeneralKnowledgeCategory.objects.get(category='Sport')
                        base_query = base_query.filter(category=category)

                    # Special filtering for Music round based on player ages
                    if round_name == "Music":
                        # Check if any players are born before 1990
                        from datetime import date
                        cutoff_date = date(1990, 1, 1)
                        has_older_players = Player.objects.filter(player_dob__lt=cutoff_date).exists()
                        if has_older_players:
                            # Exclude modern music for older audiences
                            base_query = base_query.filter(modern_music=False)

                    # Apply exclusion filter
                    if exclude_previous:
                        previous_questions = Quiz.objects.values_list('random_numbers', flat=True)
                        previous_question_ids = set()
                        for pq in previous_questions:
                            if pq and isinstance(pq, dict):
                                for key, value in pq.items():
                                    if isinstance(value, list):
                                        if any(isinstance(x, list) for x in value):
                                            flattened = [item for sublist in value for item in (sublist if isinstance(sublist, list) else [sublist])]
                                            previous_question_ids.update(flattened)
                                        else:
                                            previous_question_ids.update(value)
                                    else:
                                        previous_question_ids.add(value)
                        base_query = base_query.exclude(id__in=previous_question_ids)

                    # Get final IDs
                    ids = list(base_query.values_list('id', flat=True))

                    # Apply random selection
                    if ids:
                        if round_name == "Who is the Oldest":
                            random.shuffle(ids)
                            random_numbers[round_name] = [ids[i:i + 5] for i in range(0, min(50, len(ids)), 5) if len(ids[i:i + 5]) == 5][:10]
                        else:
                            random_numbers[round_name] = random.sample(ids, min(10, len(ids)))

            quiz.random_numbers = random_numbers
            quiz.save()
            
            # Display the join code to the user
            messages.success(request, f'Quiz ready! Join code: {quiz.join_code}')
            return redirect('active_quiz:active_quiz')
        else:
            print("Form Errors:", quiz_selection_form.errors)
    else:
        quiz_selection_form = QuizSelectionForm()

    context = {
        'users': users,
        'rounds': rounds,
        'quiz_selection_form': quiz_selection_form,
        'latest_quiz': latest_quiz,
        'current_players': current_players,
        'question_counts': question_counts,  # Add the counts to the context
    }
    return render(request, 'quiz_site/quiz_home.html', context)


@login_required
def check_players_update(request):
    """
    Check if new players have joined the quiz since the last check
    """
    quiz = Quiz.objects.latest('date_created')
    
    # Get current player count from session
    current_player_count = request.session.get('player_count', 0)
    current_player_ids = set(request.session.get('player_ids', []))
    
    # Get actual players from database
    actual_players = quiz.players.all()
    actual_player_count = actual_players.count()
    actual_player_ids = set(player.id for player in actual_players)
    
    # Update session with current values
    request.session['player_count'] = actual_player_count
    request.session['player_ids'] = list(actual_player_ids)
    
    # Return whether an update is needed
    return JsonResponse({
        'update': current_player_count != actual_player_count or current_player_ids != actual_player_ids
    })


def loading_page(request):
    """
    Display a loading page before redirecting to the active quiz
    """
    return render(request, 'quiz_site/loading.html')


def check_quiz_started(request):
    """
    Check if the quiz has started (rounds have been selected and quiz is active)
    """
    try:
        quiz = Quiz.objects.latest('date_created')
        # Quiz is considered "started" if it has rounds selected and question_counter >= 0
        # Or if rounds exist and random_numbers have been generated
        started = quiz.rounds.exists() and quiz.random_numbers
        return JsonResponse({'started': started})
    except Quiz.DoesNotExist:
        return JsonResponse({'started': False})

    
# -------------------------------------------------------------------------------
# ----------------------------- Question Models ---------------------------------
# -------------------------------------------------------------------------------

def general_knowledge(request):
    users = User.objects.all()
    categories = GeneralKnowledgeCategory.objects.all()
    selected_category = request.GET.get('category', None)
    
    if selected_category:
        general_knowledge = GeneralKnowledge.objects.filter(category_id=selected_category)
    else:
        general_knowledge = GeneralKnowledge.objects.all()

    general_knowledge_form = GeneralKnowledgeForm()

    # Count questions per category
    category_counts = {category.category: 0 for category in categories}
    for question in GeneralKnowledge.objects.all():
        if question.category:
            category_counts[question.category.category] += 1
        else:
            category_counts['Uncategorized'] = category_counts.get('Uncategorized', 0) + 1

    if request.method == 'POST':
        general_knowledge_form = GeneralKnowledgeForm(request.POST, request.FILES)
        if general_knowledge_form.is_valid():
            general_knowledge = general_knowledge_form.save(commit=False)
            general_knowledge.save()
            messages.success(request, 'Question added successfully.')
            
            # Get selected_tab and redirect back to the same category
            selected_tab = request.POST.get('selected_tab', '')
            if selected_tab:
                from django.urls import reverse
                return redirect(f"{reverse('general_knowledge')}?category={selected_tab}")
            return redirect('general_knowledge')

    total_questions_count = sum(category_counts.values())

    context = {
        'general_knowledge': general_knowledge,
        'general_knowledge_form': general_knowledge_form,
        'users': users,
        'categories': categories,
        'category_counts': category_counts,
        'selected_category': selected_category,
        'total_questions_count': total_questions_count,
    }

    return render(request, 'quiz_site/general_knowledge.html', context)


def edit_general_knowledge(request, question_id):
    users = User.objects.all()
    question = get_object_or_404(GeneralKnowledge, pk=question_id)
    categories = GeneralKnowledgeCategory.objects.all()
    general_knowledge_form = GeneralKnowledgeForm(instance=question)

    if request.method == 'POST':
        edit_general_knowledge_form = GeneralKnowledgeForm(request.POST, request.FILES, instance=question)
        print(edit_general_knowledge_form.errors)
        if edit_general_knowledge_form.is_valid():
            question = edit_general_knowledge_form.save(commit=False)
            question.category = edit_general_knowledge_form.cleaned_data['category']
            question.save()
            messages.success(request, 'Question edited successfully.')
            print('Question edited successfully')
            
            # Redirect back to the appropriate category page
            if question.category:
                category_name = question.category.category
                category_url_map = {
                    'General': 'general',
                    'Science': 'science',
                    'Geography': 'geography',
                    'History': 'history',
                    'Entertainment': 'entertainment',
                    'Pop Culture': 'entertainment',  # Merged with Entertainment
                    'Maths': 'maths',
                    'Mythology': 'mythology',
                    'Technology': 'technology',
                    'Sport': 'sport',
                }
                redirect_url = category_url_map.get(category_name, 'general_knowledge')
                return redirect(redirect_url)
            
            return redirect('general_knowledge')

    context = {
        'general_knowledge': general_knowledge,
        'general_knowledge_form': general_knowledge_form,
        'users': users,
        'categories': categories,
    }

    return render(request, 'quiz_site/general_knowledge.html', context)


def delete_general_knowledge(request, question_id):
    """
    View to delete a specific general knowledge question from the database
    """
    question = get_object_or_404(GeneralKnowledge, pk=question_id)
    question_text = question.question  # Store the question before deletion for the message
    question.delete()
    messages.success(request, f'Question "{question_text}" deleted successfully.')
    
    return redirect('general_knowledge')


# Separate views for each General Knowledge category
def general(request):
    return _category_view(request, 'General', 'general.html')

def science(request):
    return _category_view(request, 'Science', 'science.html')

def geography(request):
    return _category_view(request, 'Geography', 'geography.html')

def history(request):
    return _category_view(request, 'History', 'history.html')

def entertainment(request):
    """Entertainment view - now includes Pop Culture questions"""
    users = User.objects.all()
    # Get both Entertainment and Pop Culture categories
    questions = GeneralKnowledge.objects.none()
    categories = []
    
    try:
        entertainment_cat = GeneralKnowledgeCategory.objects.get(category='Entertainment')
        questions = questions | GeneralKnowledge.objects.filter(category=entertainment_cat)
        categories.append(entertainment_cat)
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    try:
        pop_culture_cat = GeneralKnowledgeCategory.objects.get(category='Pop Culture')
        questions = questions | GeneralKnowledge.objects.filter(category=pop_culture_cat)
        categories.append(pop_culture_cat)
    except GeneralKnowledgeCategory.DoesNotExist:
        pass
    
    form = GeneralKnowledgeForm()
    
    if request.method == 'POST':
        form = GeneralKnowledgeForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            # Default to Entertainment category if it exists
            if categories:
                question.category = categories[0]
            question.save()
            messages.success(request, 'Question added successfully.')
            return redirect(request.path)
    
    context = {
        'general_knowledge': questions,
        'general_knowledge_form': form,
        'users': users,
        'category_name': 'Entertainment & Pop Culture',
        'question_count': questions.count(),
    }
    
    return render(request, 'quiz_site/entertainment.html', context)

def maths(request):
    return _category_view(request, 'Maths', 'maths.html')

def pop_culture(request):
    """Redirect to entertainment view since they're now merged"""
    return redirect('entertainment')

def mythology(request):
    return _category_view(request, 'Mythology', 'mythology.html')

def technology(request):
    return _category_view(request, 'Technology', 'technology.html')

def sport(request):
    return _category_view(request, 'Sport', 'sport.html')

def _category_view(request, category_name, template_name):
    """
    Helper function to handle category-specific views
    """
    users = User.objects.all()
    try:
        category = GeneralKnowledgeCategory.objects.get(category=category_name)
        questions = GeneralKnowledge.objects.filter(category=category)
    except GeneralKnowledgeCategory.DoesNotExist:
        questions = GeneralKnowledge.objects.none()
    
    form = GeneralKnowledgeForm()

    if request.method == 'POST':
        form = GeneralKnowledgeForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.category = category
            question.save()
            messages.success(request, 'Question added successfully.')
            return redirect(request.path)

    context = {
        'general_knowledge': questions,
        'general_knowledge_form': form,
        'users': users,
        'category_name': category_name,
    }

    return render(request, f'quiz_site/{template_name}', context)


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
    logos = Logos.objects.all().order_by('company')
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


def delete_logos(request, logo_id):
    """
    View to delete a specific logo from the database
    """
    logo = get_object_or_404(Logos, pk=logo_id)
    logo_name = logo.company  # Store the name before deletion for the message
    logo.delete()
    messages.success(request, f'Logo "{logo_name}" deleted successfully.')
    
    return redirect('logos')


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

    # Sort the actor choices alphabetically
    movie_form.fields['actors'].choices = sorted(movie_form.fields['actors'].choices, key=lambda choice: choice[1])

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
    location = get_object_or_404(Locations, pk=location_id)
    locations = Locations.objects.all()
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


def delete_locations(request, location_id):
    """
    View to delete a specific location from the database
    """
    location = get_object_or_404(Locations, pk=location_id)
    location_name = location.location  # Store the name before deletion for the message
    location.delete()
    messages.success(request, f'Location "{location_name}" deleted successfully.')
    
    return redirect('locations')


def music(request):
    users = User.objects.all()
    music_list = Music.objects.all()
    music_form = MusicForm()

    if request.method == 'POST':
        if 'music_id' in request.POST:
            music = get_object_or_404(Music, pk=request.POST['music_id'])
            music_form = MusicForm(request.POST, request.FILES, instance=music)
            if music_form.is_valid():
                music = music_form.save(commit=False)
                music.save()
                messages.success(request, 'Music edited successfully.')
                return redirect('music')
        else:
            music_form = MusicForm(request.POST, request.FILES)
            if music_form.is_valid():
                music = music_form.save(commit=False)
                music.save()
                messages.success(request, 'Music added successfully.')
                return redirect('music')

    context = {
        'music_list': music_list,
        'music_form': music_form,
        'users': users,
    }

    return render(request, 'quiz_site/music.html', context)


def edit_music(request, music_id):
    music = get_object_or_404(Music, pk=music_id)
    music_form = MusicForm(instance=music)

    if request.method == 'POST':
        music_form = MusicForm(request.POST, request.FILES, instance=music)
        if music_form.is_valid():
            music = music_form.save(commit=False)
            music.save()
            messages.success(request, 'Music edited successfully.')
            return redirect('music')
        else:
            print(music_form.errors)

    context = {
        'music_form': music_form,
        'music': music,
    }

    return render(request, 'quiz_site/edit_music.html', context)


@login_required
def rounds(request):
    """
    View to display all rounds with their disabled/active status
    """
    active_rounds = Rounds.objects.filter(disabled=False).order_by('question_type')
    disabled_rounds = Rounds.objects.filter(disabled=True).order_by('question_type')
    
    # Handle form submissions
    if request.method == 'POST':
        if 'add_round' in request.POST:
            # Add new round
            form = RoundsForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Round added successfully.')
                return redirect('rounds')
        elif 'edit_round' in request.POST:
            # Edit existing round
            round_id = request.POST.get('round_id')
            round_obj = get_object_or_404(Rounds, id=round_id)
            form = RoundsForm(request.POST, instance=round_obj)
            if form.is_valid():
                form.save()
                messages.success(request, 'Round updated successfully.')
                return redirect('rounds')
        elif 'toggle_round' in request.POST:
            # Toggle active/disabled status
            round_id = request.POST.get('round_id')
            round_obj = get_object_or_404(Rounds, id=round_id)
            round_obj.disabled = not round_obj.disabled
            round_obj.save()
            status = "disabled" if round_obj.disabled else "enabled"
            messages.success(request, f'Round {status} successfully.')
            return redirect('rounds')
    
    # Forms for the template
    add_form = RoundsForm()
    
    context = {
        'active_rounds': active_rounds,
        'disabled_rounds': disabled_rounds,
        'add_form': add_form,
        'active_count': active_rounds.count(),
        'disabled_count': disabled_rounds.count(),
    }
    
    return render(request, 'quiz_site/rounds.html', context)


@login_required
def manage_users(request):
    """View for managing users - viewing profiles, resetting passwords, etc."""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        if action == 'reset_password' and user_id:
            try:
                user = User.objects.get(id=user_id)
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')

                if not new_password or not confirm_password:
                    return JsonResponse({'success': False, 'error': 'Both password fields are required'})

                if new_password != confirm_password:
                    return JsonResponse({'success': False, 'error': 'Passwords do not match'})

                if len(new_password) < 8:
                    return JsonResponse({'success': False, 'error': 'Password must be at least 8 characters long'})

                user.set_password(new_password)
                user.save()

                messages.success(request, f'Password reset successfully for {user.username}')
                return JsonResponse({'success': True})

            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'User not found'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})

        elif action == 'upload_photo' and user_id and request.FILES.get('photo'):
            try:
                user = User.objects.get(id=user_id)
                player, created = Player.objects.get_or_create(user=user)

                player.player_photo = request.FILES['photo']
                player.save()

                messages.success(request, f'Profile photo uploaded successfully for {user.username}')
                return JsonResponse({'success': True, 'photo_url': player.player_photo.url})

            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'User not found'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})

        elif action == 'set_dob' and user_id and request.POST.get('date_of_birth'):
            try:
                user = User.objects.get(id=user_id)
                player, created = Player.objects.get_or_create(user=user)
                
                from datetime import datetime
                dob_str = request.POST.get('date_of_birth')
                player.player_dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                player.save()

                messages.success(request, f'Date of birth set successfully for {user.username}')
                return JsonResponse({'success': True})

            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'User not found'})
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid date format'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})

        elif action == 'delete_user' and user_id:
            try:
                user = User.objects.get(id=user_id)
                username = user.username
                user.delete()

                messages.success(request, f'User {username} has been deleted successfully')
                return JsonResponse({'success': True})

            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'User not found'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})

    users = User.objects.all().order_by('username')
    user_profiles = []

    for user in users:
        try:
            player = Player.objects.get(user=user)
            has_photo = bool(player.player_photo)
            photo_url = player.player_photo.url if has_photo else None
        except Player.DoesNotExist:
            player = None
            has_photo = False
            photo_url = None

        user_profiles.append({
            'user': user,
            'player': player,
            'has_photo': has_photo,
            'photo_url': photo_url,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
        })

    context = {
        'user_profiles': user_profiles,
        'total_users': users.count(),
    }

    return render(request, 'quiz_site/manage_users.html', context)


@login_required
def user_profile(request):
    """View for users to manage their own profile"""
    user = request.user
    player, created = Player.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'upload_photo' and request.FILES.get('photo'):
            try:
                player.player_photo = request.FILES['photo']
                player.save()
                messages.success(request, 'Profile photo updated successfully!')
                return redirect('user_profile')
            except Exception as e:
                messages.error(request, f'Error uploading photo: {str(e)}')
        
        elif action == 'update_username' and request.POST.get('username'):
            try:
                new_username = request.POST.get('username').strip()
                if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                    messages.error(request, 'Username already taken')
                else:
                    user.username = new_username
                    user.save()
                    messages.success(request, 'Username updated successfully!')
                return redirect('user_profile')
            except Exception as e:
                messages.error(request, f'Error updating username: {str(e)}')
        
        elif action == 'update_email':
            try:
                new_email = request.POST.get('email', '').strip()
                user.email = new_email
                user.save()
                messages.success(request, 'Email updated successfully!')
                return redirect('user_profile')
            except Exception as e:
                messages.error(request, f'Error updating email: {str(e)}')
        
        elif action == 'update_dob' and request.POST.get('date_of_birth'):
            try:
                from datetime import datetime
                dob_str = request.POST.get('date_of_birth')
                player.player_dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                player.save()
                messages.success(request, 'Date of birth updated successfully!')
                return redirect('user_profile')
            except ValueError:
                messages.error(request, 'Invalid date format')
            except Exception as e:
                messages.error(request, f'Error updating date of birth: {str(e)}')
        
        elif action == 'change_password':
            try:
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                
                # Validate new password
                if new_password != confirm_password:
                    messages.error(request, 'New passwords do not match')
                    return redirect('user_profile')
                
                if len(new_password) < 8:
                    messages.error(request, 'Password must be at least 8 characters long')
                    return redirect('user_profile')
                
                # Change password
                user.set_password(new_password)
                user.save()
                
                # Re-authenticate the user
                from django.contrib.auth import login
                login(request, user)
                
                messages.success(request, 'Password changed successfully!')
                return redirect('user_profile')
                
            except Exception as e:
                messages.error(request, f'Error changing password: {str(e)}')
    
    context = {
        'user': user,
        'player': player,
    }
    
    return render(request, 'quiz_site/profile.html', context)
