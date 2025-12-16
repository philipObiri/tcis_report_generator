from django import forms
from .models import Score
from django.forms import modelformset_factory
from decimal import Decimal

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = [
            'class_work_score', 'progressive_test_1_score', 'progressive_test_2_score',
            'progressive_test_3_score', 'midterm_score', 'exam_score'
        ]

    def clean(self):
        cleaned_data = super().clean()

        # Get the individual score fields
        class_work_score = cleaned_data.get('class_work_score')
        progressive_test_1_score = cleaned_data.get('progressive_test_1_score')
        progressive_test_2_score = cleaned_data.get('progressive_test_2_score')
        progressive_test_3_score = cleaned_data.get('progressive_test_3_score')
        midterm_score = cleaned_data.get('midterm_score')
        exam_score = cleaned_data.get('exam_score')

        # Ensure the scores are within valid ranges (0-100)
        for field_name, score in [
            ('class_work_score', class_work_score),
            ('progressive_test_1_score', progressive_test_1_score),
            ('progressive_test_2_score', progressive_test_2_score),
            ('progressive_test_3_score', progressive_test_3_score),
            ('midterm_score', midterm_score),
            ('exam_score', exam_score)
        ]:
            if score is not None and (score < 0 or score > 100):
                self.add_error(field_name, f"{field_name.replace('_', ' ').title()} must be between 0 and 100.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Note: Calculation logic has been moved to the Score model's save() method
        # to support both Standard and Cambridge grading systems.
        # The model will automatically calculate continuous_assessment, total_score,
        # and grade based on the subject's grading_system configuration.

        if commit:
            instance.save()

        return instance

    # Add the delete checkbox for formsets (if needed)
    DELETE = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

# Create the formset
ScoreFormSet = modelformset_factory(Score, form=ScoreForm, extra=0)
