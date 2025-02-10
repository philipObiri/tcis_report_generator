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

        # Calculate the Continuous Assessment score: 30% of the total of the individual scores
        continuous_assessment = (instance.class_work_score + 
                                 instance.progressive_test_1_score + 
                                 instance.progressive_test_2_score + 
                                 instance.progressive_test_3_score + 
                                 instance.midterm_score)

        instance.continuous_assessment = continuous_assessment * Decimal('0.30')

        # Calculate the Total Score: 30% of Continuous Assessment + 70% of Exam Score
        instance.total_score = (instance.continuous_assessment + (instance.exam_score * Decimal('0.70')))

        # Save the grade based on the total score
        if instance.total_score >= Decimal('90'):
            instance.grade = 'A*'
        elif instance.total_score >= Decimal('80'):
            instance.grade = 'A'
        elif instance.total_score >= Decimal('70'):
            instance.grade = 'B'
        elif instance.total_score >= Decimal('60'):
            instance.grade = 'C'
        elif instance.total_score >= Decimal('50'):
            instance.grade = 'D'
        else:
            instance.grade = 'F'

        if commit:
            instance.save()

        return instance

    # Add the delete checkbox for formsets (if needed)
    DELETE = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

# Create the formset
ScoreFormSet = modelformset_factory(Score, form=ScoreForm, extra=0)
