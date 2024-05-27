from django.shortcuts import render
from django.http import HttpResponse
from .models import *


# Create your views here.
def quiz_home(request):
    q_categories = QuestionCategory.objects.all()

    context = {
        'q_categories': q_categories
    }

    return render(request, 'quiz_site/quiz_home.html', context)