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


class LogoForm(forms.ModelForm):
    class Meta:
        model = Logos
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].initial = QuestionCategory.objects.get(category='Guess the Logo')
        self.fields['created_by'].initial = User.objects.get(player_name='David')


class JetForm(forms.ModelForm):
    class Meta:
        model = Jets
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].initial = QuestionCategory.objects.get(category='Guess the Jet')
        self.fields['created_by'].initial = User.objects.get(player_name='David')


class CelebrityForm(forms.ModelForm):
    class Meta:
        model = Celebrities
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].initial = QuestionCategory.objects.get(category='Guess the Celebrity')
        self.fields['created_by'].initial = User.objects.get(player_name='David')


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
        self.fields['category'].initial = QuestionCategory.objects.get(category='Guess the Movie')
        self.fields['created_by'].initial = User.objects.get(player_name='David')