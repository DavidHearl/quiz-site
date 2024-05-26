from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class User(models.Model):
    player_name = models.CharField(max_length=100)
    player_score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.player_name


class Quiz(models.Model):
    players = models.ManyToManyField(User)

    def __str__(self):
        return self.players


class QuestionCategory(models.Model):
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.category


# Questions
class PictureQuestion(models.Model):
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE,null=True,  blank=True)
    question = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    difficulty = models.FloatField()
    image = models.ImageField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    choice_1 = models.CharField(max_length=100)
    choice_2 = models.CharField(max_length=100)
    choice_3 = models.CharField(max_length=100)
    choice_4 = models.CharField(max_length=100)

    def __str__(self):
        return self.question


class MultipleChoice(models.Model):
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE,null=True,  blank=True)
    question = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    difficulty = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    choice_1 = models.CharField(max_length=100)
    choice_2 = models.CharField(max_length=100)
    choice_3 = models.CharField(max_length=100)
    choice_4 = models.CharField(max_length=100)

    def __str__(self):
        return self.question


class TrueFalseQuestion(models.Model):
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE,null=True,  blank=True)
    question = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    difficulty = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    true_statement = models.CharField(max_length=100)
    false_statement = models.CharField(max_length=100)

    def __str__(self):
        return self.question

