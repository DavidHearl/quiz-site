from django.db import models


# Create your models here.
class User(models.Model):
    player_name = models.CharField(max_length=100)
    player_score = models.IntegerField()


class Quiz(models.Model):
    players = models.ManyToManyField(User)


class QuestionCategory(models.Model):
    category = models.CharField(max_length=100)


# Questions
class PictureQuestion(models.Model):
    question = models.CharField()
    answer = models.CharField()
    difficulty = models.FloatField()
    image = models.ImageField()
    created_by = model.ForeignKey(User)

    choice_1 = models.CharField(max_length=100)
    choice_2 = models.CharField(max_length=100)
    choice_3 = models.CharField(max_length=100)
    choice_4 = models.CharField(max_length=100)


class MultipleChoice(models.Model):
    question = models.CharField()
    answer = models.CharField()
    difficulty = models.FloatField()
    created_by = model.ForeignKey(User)

    choice_1 = models.CharField(max_length=100)
    choice_2 = models.CharField(max_length=100)
    choice_3 = models.CharField(max_length=100)
    choice_4 = models.CharField(max_length=100)


class TrueFalseQuestion(models.Model):
    question = models.CharField(max_length=100)
    true_statement = models.CharField(max_length=100)
    false_statement = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
