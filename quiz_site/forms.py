from django import forms
from django.contrib.auth.models import User
from .models import *

class GeneralKnowledgeForm(forms.ModelForm):
    class Meta:
        model = GeneralKnowledge
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(player_name='David')


class TrueOrFalseForm(forms.ModelForm):
    class Meta:
        model = TrueOrFalse
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(player_name='David')
        

class FlagForm(forms.ModelForm):
    class Meta:
        model = Flags
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(player_name='David')


class LogoForm(forms.ModelForm):
    class Meta:
        model = Logos
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(player_name='David')


class JetForm(forms.ModelForm):
    class Meta:
        model = Jets
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(player_name='David')


class CelebrityForm(forms.ModelForm):
    class Meta:
        model = Celebrities
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        self.fields['created_by'].initial = User.objects.get(player_name='David')


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = User.objects.get(player_name='David')