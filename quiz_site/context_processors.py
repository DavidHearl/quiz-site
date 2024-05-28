from .models import *

def categories(request):
    return {'categories': QuestionCategory.objects.all()}