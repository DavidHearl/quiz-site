from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.fields import JSONField


# User model, used to store player names and scores
class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    player_score = models.FloatField(default=0.0)
    incorrect_answers = models.IntegerField(default=0)
    number_of_questions = models.IntegerField(default=0)
    player_photo = models.ImageField(upload_to='player_photos', blank=True, null=True)
    QUESTION_STATUS_CHOICES = [
        (0, 'Not Answered'),
        (1, 'Correct'),
        (2, 'Incorrect'),
        (3, 'Partial')
    ]
    question_answered = models.IntegerField(choices=QUESTION_STATUS_CHOICES, default=0)
    answers = models.JSONField(default=dict, blank=True, null=True)
    points = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.user.username


# Rounds model, used to store the different types of questions that can be asked
class Rounds(models.Model):
    question_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True, help_text="Description of what this round entails")
    selected = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.question_type


# Quiz model, used to create the game and assign the players playing the game
class Quiz(models.Model):
    quiz_name = models.CharField(max_length=100, default="Quiz")
    players = models.ManyToManyField(User)
    rounds = models.ManyToManyField(Rounds)
    random_numbers = models.JSONField(default=list, blank=True, null=True)
    question_counter = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    correct_answers = models.JSONField(default=dict)
    current_round = models.OneToOneField(Rounds, on_delete=models.CASCADE, blank=True, null=True, related_name='current_quiz_round')
    join_code = models.CharField(max_length=4, blank=True, null=True, unique=True)
    countdown_start_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.quiz_name

# Category for general knowledge, used for various categories eg sport, science etc
class GeneralKnowledgeCategory(models.Model):
    category = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.category

# -------------------------------------------------------------------------------
# ---------------------------- Question Database --------------------------------
# -------------------------------------------------------------------------------

class GeneralKnowledge(models.Model):
    # Question and Answer
    question = models.CharField(max_length=128)
    answer = models.CharField(max_length=100)
    category = models.ForeignKey(GeneralKnowledgeCategory, on_delete=models.CASCADE, blank=True, null=True)

    # Multiple Choice Answers
    choice_1 = models.CharField(max_length=100, null=True, blank=True)
    choice_2 = models.CharField(max_length=100, null=True, blank=True)
    choice_3 = models.CharField(max_length=100, null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True, default=0.5)

    def __str__(self):
        return f"({self.id}) {self.question}"


class TrueOrFalse(models.Model):
    # Question and Answer
    question = models.CharField(max_length=128)
    answer = models.BooleanField()

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True, default=0.5)

    def __str__(self):
        return self.question


class Flags(models.Model):
    # Answers
    country = models.CharField(max_length=100, null=True, blank=True)
    capital = models.CharField(max_length=100, null=True, blank=True)
    flag = models.ImageField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True, default=0.5)

    def __str__(self):
        if self.country:
            return f"({self.id}) {self.country}"
        

class Logos(models.Model):
    # Answers
    company = models.CharField(max_length=100)
    logo = models.ImageField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True, default=0.5)

    def __str__(self):
        if self.company:
            return self.company if self.company else ''


class Jets(models.Model):
    # Answers
    name = models.CharField(max_length=100)
    code_name = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True, default=0.5)

    def __str__(self):
        if self.name:
            return self.name if self.name else ''
        

class Celebrities(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True, default=0.5)

    def __str__(self):
        full_name = self.first_name + " " + self.last_name
        return f"({self.id}) {full_name}"


class Movies(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    poster = models.ImageField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    actors = models.ManyToManyField(Celebrities)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True, default=0.5)

    def __str__(self):
        return self.title


class Locations(models.Model):
    # Answers
    location = models.CharField(max_length=100)
    photo = models.ImageField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True, default=0.5)

    def __str__(self):
        return self.location


class Music(models.Model):
    # Answers
    artist = models.CharField(max_length=100)
    song_title = models.CharField(max_length=100)
    audio_file = models.FileField(upload_to='music_files', null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True, blank=True, default=0.5)

    def __str__(self):
        return self.song_title

