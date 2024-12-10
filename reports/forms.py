from django import forms
from .models import Score
from django.forms import modelformset_factory


class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ['continuous_assessment', 'exam_score']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.total_score = (instance.continuous_assessment * 0.3) + (instance.exam_score * 0.7)
        if commit:
            instance.save()
        return instance

    # Add the delete checkbox for formsets
    DELETE = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

# Create the formset
ScoreFormSet = modelformset_factory(Score, form=ScoreForm, extra=0)
