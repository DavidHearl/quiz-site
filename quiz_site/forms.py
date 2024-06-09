from django import forms
from django.contrib.auth.models import User
from .models import *

class FlagForm(forms.ModelForm):
    class Meta:
        model = Flags
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].initial = QuestionCategory.objects.get(category='Guess the Flag')
        self.fields['created_by'].initial = User.objects.get(player_name='David')


class LogosForm(forms.ModelForm):
    class Meta:
        model = Logos
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].initial = QuestionCategory.objects.get(category='Guess the Logos')
        self.fields['created_by'].initial = User.objects.get(player_name='David')