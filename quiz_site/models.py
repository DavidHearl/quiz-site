from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# User model, used to store player names and scores
class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    player_score = models.IntegerField(null=True, blank=True)
    participating = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


# Rounds model, used to store the different types of questions that can be asked
class Rounds(models.Model):
    question_type = models.CharField(max_length=100)
    selected = models.BooleanField(default=False)

    def __str__(self):
        return self.question_type


# Quiz model, used to create the game and assign the players playing the game
class Quiz(models.Model):
    quiz_name = models.CharField(max_length=100, default="Quiz")
    players = models.ManyToManyField(User)
    rounds = models.ManyToManyField(Rounds)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.quiz_name

# -------------------------------------------------------------------------------
# ----------------------------- Question Models ---------------------------------
# -------------------------------------------------------------------------------
class Questions(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)

    movie_release_dates = models.ManyToManyField('GeneralKnowledge', blank=True, related_name='movie_release_date_questions')
    who_is_the_imposter = models.ManyToManyField('Celebrities', blank=True, related_name='imposter_questions')
    who_is_the_oldest = models.ManyToManyField('Celebrities', blank=True, related_name='oldest_questions')
    true_or_false = models.ManyToManyField('TrueOrFalse', blank=True, related_name='true_or_false_questions')
    guess_the_age = models.ManyToManyField('Celebrities', blank=True, related_name='guess_the_age_questions')
    movies = models.ManyToManyField('Movies', blank=True, related_name='movie_questions')
    logos = models.ManyToManyField('Logos', blank=True, related_name='logo_questions')
    locations = models.ManyToManyField('Locations', blank=True, related_name='location_questions')
    fight_jets = models.ManyToManyField('Jets', blank=True, related_name='fight_jet_questions')
    celebrities = models.ManyToManyField('Celebrities', blank=True, related_name='celebrity_questions')
    capitals = models.ManyToManyField('Flags', blank=True, related_name='capital_questions')
    general_knowledge = models.ManyToManyField('GeneralKnowledge', blank=True, related_name='general_knowledge_questions')
    flags = models.ManyToManyField('Flags', blank=True, related_name='flag_questions')

    def __str__(self):
        return self.quiz.quiz_name

# -------------------------------------------------------------------------------
# ---------------------------- Question Database --------------------------------
# -------------------------------------------------------------------------------

class GeneralKnowledge(models.Model):
    # Question and Answer
    question = models.CharField(max_length=128)
    answer = models.CharField(max_length=100)

    # Multiple Choice Answers
    choice_1 = models.CharField(max_length=100, null=True, blank=True)
    choice_2 = models.CharField(max_length=100, null=True, blank=True)
    choice_3 = models.CharField(max_length=100, null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.question


class TrueOrFalse(models.Model):
    # Question and Answer
    question = models.CharField(max_length=128)
    answer = models.BooleanField()

    # Question Stats
    difficulty = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.question


class Flags(models.Model):
    # Answers
    country = models.CharField(max_length=100, null=True, blank=True)
    capital = models.CharField(max_length=100, null=True, blank=True)
    flag = models.ImageField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True, default=0.5)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if self.country:
            return self.country
        

class Logos(models.Model):
    # Answers
    company = models.CharField(max_length=100)
    logo = models.ImageField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if self.company:
            return self.company if self.company else ''


class Jets(models.Model):
    # Answers
    name = models.CharField(max_length=100)
    code_name = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if self.name:
            return self.name if self.name else ''
        

class Celebrities(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        full_name = self.first_name + " " + self.last_name
        return full_name


class Movies(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    poster = models.ImageField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    actors = models.ManyToManyField(Celebrities)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Locations(models.Model):
    # Answers
    location = models.CharField(max_length=100)
    photo = models.ImageField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.location
