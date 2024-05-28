from django.db import models
from django.contrib.auth.models import User


# User model, used to store player names and scores
class User(models.Model):
    player_name = models.CharField(max_length=100)
    player_score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.player_name


# Quiz model, used to create the game and assign the players playing the game
class Quiz(models.Model):
    players = models.ManyToManyField(User)
    question_set = models.ManyToManyField('QuestionCategory')

    def __str__(self):
        return self.players


# Question Category model, used to categorize the questions
class QuestionCategory(models.Model):
    category = models.CharField(max_length=100)
    category_question = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.category


# -------------------------------------------------------------------------------
# ----------------------------- Question Models ---------------------------------
# -------------------------------------------------------------------------------

class GeneralKnowledge(models.Model):
    # Question Category
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, null=True,  blank=True)

    # Question and Answer
    question = models.CharField(max_length=128)
    answer = models.CharField(max_length=100)

    # Question Stats
    difficulty = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.question


class GuessTheFlag(models.Model):
    # Question Category
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, null=True,  blank=True)

    # Answers
    country = models.CharField(max_length=100, null=True, blank=True)
    capital = models.CharField(max_length=100, null=True, blank=True)
    flag = models.ImageField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.country


# Multiple Choice Questions
# class PictureQuestion(models.Model):
#     category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, null=True,  blank=True)
#     answer = models.CharField(max_length=100)
#     difficulty = models.FloatField(null=True,  blank=True)
#     image = models.ImageField()
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE)

#     choice_1 = models.CharField(max_length=100, null=True,  blank=True)
#     choice_2 = models.CharField(max_length=100, null=True,  blank=True)
#     choice_3 = models.CharField(max_length=100, null=True,  blank=True)
#     choice_4 = models.CharField(max_length=100, null=True,  blank=True)

#     def __str__(self):
#         return f"{self.category.category} - {self.answer}"


# class MultipleChoice(models.Model):
#     category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE,null=True,  blank=True)
#     answer = models.CharField(max_length=100)
#     difficulty = models.FloatField(null=True,  blank=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE)

#     choice_1 = models.CharField(max_length=100, null=True,  blank=True)
#     choice_2 = models.CharField(max_length=100, null=True,  blank=True)
#     choice_3 = models.CharField(max_length=100, null=True,  blank=True)
#     choice_4 = models.CharField(max_length=100, null=True,  blank=True)

#     def __str__(self):
#         return f"{self.category.category} - {self.answer}"


# True or False Questions
# class TrueFalseQuestion(models.Model):
#     category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE,null=True,  blank=True)
#     question = models.CharField(max_length=128)
#     answer = models.CharField(max_length=100)
#     difficulty = models.FloatField(null=True,  blank=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE)

#     true_statement = models.CharField(max_length=100)
#     false_statement = models.CharField(max_length=100)

#     def __str__(self):
#         return self.question


