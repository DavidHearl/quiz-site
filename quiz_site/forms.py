from django import forms
from django.contrib.auth.models import User
from .models import *

class QuizSelectionForm(forms.Form):
    class Meta:
        model = Quiz
        fields = ['quiz_name']

    quiz_name = forms.CharField(max_length=200)
    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple)
    rounds = forms.ModelMultipleChoiceField(queryset=Rounds.objects.all(), widget=forms.CheckboxSelectMultiple)


# -------------------------------------------------------------------------------
# --------------------------- Question Models -----------------------------------
# -------------------------------------------------------------------------------

class GeneralKnowledgeForm(forms.ModelForm):
    class Meta:
        model = GeneralKnowledge
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(username='david')


class TrueOrFalseForm(forms.ModelForm):
    class Meta:
        model = TrueOrFalse
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(username='david')
        

class FlagForm(forms.ModelForm):
    class Meta:
        model = Flags
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(username='david')


class LogoForm(forms.ModelForm):
    class Meta:
        model = Logos
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(username='david')


class JetForm(forms.ModelForm):
    class Meta:
        model = Jets
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(username='david')


class CelebrityForm(forms.ModelForm):
    class Meta:
        model = Celebrities
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(username='david')


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
        self.fields['created_by'].initial = User.objects.get(username='david')


class LocationForm(forms.ModelForm):
    class Meta:
        model = Locations
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(username='david')