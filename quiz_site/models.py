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


class Flags(models.Model):
    # Question Category
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, null=True,  blank=True)

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
    # Question Category
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, null=True,  blank=True)

    # Answers
    company = models.CharField(max_length=100)
    logo = models.ImageField(null=True, blank=True)

    # Question Stats
    difficulty = models.FloatField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if self.company:
            return self.company if self.company else ''
        

# class Celebrities(models.Model):
#     # Question Category
#     category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, null=True,  blank=True)

#     first_name = models.CharField(max_length=100, null=True, blank=True)
#     last_name = models.CharField(max_length=100, null=True, blank=True)
#     photo = models.ImageField(null=True, blank=True)

#     # Question Stats
#     difficulty = models.FloatField(null=True,  blank=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE)

#     def __str__(self):
#         full_name = self.first_name + " " + self.last_name

#         return full_name


# class Movies(models.Model):
#     # Question Category
#     category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, null=True,  blank=True)

#     name = models.CharField(max_length=100, null=True, blank=True)
#     actors = models.ManyToManyField(Celebrities)
