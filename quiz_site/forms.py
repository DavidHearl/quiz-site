from django import forms
from django.contrib.auth.models import User
from .models import *

class QuizSelectionForm(forms.Form):
    quiz_name = forms.CharField(max_length=200)
    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple)
    rounds = forms.ModelMultipleChoiceField(queryset=Rounds.objects.all(), widget=forms.CheckboxSelectMultiple)
    exclude_previous = forms.BooleanField(required=False, label="Exclude questions from previous quizzes")

    class Meta:
        model = Quiz
        fields = ['quiz_name', 'users', 'rounds', 'exclude_previous']


# -------------------------------------------------------------------------------
# --------------------------- Question Models -----------------------------------
# -------------------------------------------------------------------------------

class GeneralKnowledgeForm(forms.ModelForm):
    class Meta:
        model = GeneralKnowledge
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TrueOrFalseForm(forms.ModelForm):
    class Meta:
        model = TrueOrFalse
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

class FlagForm(forms.ModelForm):
    class Meta:
        model = Flags
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LogoForm(forms.ModelForm):
    class Meta:
        model = Logos
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class JetForm(forms.ModelForm):
    class Meta:
        model = Jets
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CelebrityForm(forms.ModelForm):
    class Meta:
        model = Celebrities
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MovieForm(forms.ModelForm):
    actors = forms.ModelMultipleChoiceField(
        queryset=Celebrities.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Movies
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        movie = kwargs.pop('movie', None)
        super().__init__(*args, **kwargs)


class LocationForm(forms.ModelForm):
    class Meta:
        model = Locations
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MusicForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)