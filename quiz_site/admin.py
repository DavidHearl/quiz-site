from django.contrib import admin
from .models import User, Quiz, QuestionCategory, PictureQuestion, MultipleChoice, TrueFalseQuestion

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'player_name',
        'player_score'
    )

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Quiz)
admin.site.register(QuestionCategory)
admin.site.register(PictureQuestion)
admin.site.register(MultipleChoice)
admin.site.register(TrueFalseQuestion)