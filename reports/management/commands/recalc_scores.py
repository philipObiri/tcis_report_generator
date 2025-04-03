from django.core.management.base import BaseCommand
from reports.models import Score  # Replace 'app_name' with your app's name
from decimal import Decimal

class Command(BaseCommand):
    help = 'Recalculate and update scores for all Score instances in the database'

    def handle(self, *args, **kwargs):
        # Fetch all Score instances
        scores = Score.objects.all()

        # Loop through each score instance and recalculate
        for score in scores:
            self.stdout.write(f'Recalculating for {score.student.fullname} - {score.subject.name}')

            # Ensure that exam_score is never None, default to 0.0 if missing
            if score.exam_score is None:
                score.exam_score = Decimal('0.0')

            # Convert exam_score to Decimal in case it's a float or non-decimal value
            exam_score = Decimal(score.exam_score)

            # Calculate the sum of all the component scores
            total_continuous_assessment_score = (
                score.class_work_score +  # percentage score (out of 100%)
                score.progressive_test_1_score +  # percentage score (out of 100%)
                score.progressive_test_2_score +  # percentage score (out of 100%)
                score.progressive_test_3_score +  # percentage score (out of 100%)
                score.midterm_score  # percentage score (out of 100%)
            )

            # Normalize continuous_assessment to a 100% scale (total is out of 500, so divide by 500 and multiply by 100)
            normalized_continuous_assessment = (total_continuous_assessment_score / Decimal('500')) * Decimal('100')

            # Calculate Continuous Assessment as 30% of normalized value
            score.continuous_assessment = normalized_continuous_assessment * Decimal('0.30')

            # Calculate Total Score: 30% of Continuous Assessment + 70% of Exam Score
            score.total_score = (score.continuous_assessment + (exam_score * Decimal('0.70')))

            # Assign grade based on the total_score with the new grading scale
            if score.total_score >= Decimal('95') and score.total_score <= Decimal('100'):
                score.grade = 'A*'  # GPA: 4.00
            elif score.total_score >= Decimal('80') and score.total_score <= Decimal('94'):
                score.grade = 'A'   # GPA: 3.67
            elif score.total_score >= Decimal('75') and score.total_score <= Decimal('79'):
                score.grade = 'B+'  # GPA: 3.33
            elif score.total_score >= Decimal('70') and score.total_score <= Decimal('74'):
                score.grade = 'B'   # GPA: 3.00
            elif score.total_score >= Decimal('65') and score.total_score <= Decimal('69'):
                score.grade = 'C+'  # GPA: 2.67
            elif score.total_score >= Decimal('60') and score.total_score <= Decimal('64'):
                score.grade = 'C'   # GPA: 2.33
            elif score.total_score >= Decimal('50') and score.total_score <= Decimal('59'):
                score.grade = 'D'   # GPA: 2.00
            elif score.total_score >= Decimal('45') and score.total_score <= Decimal('49'):
                score.grade = 'E'   # GPA: 1.67
            elif score.total_score >= Decimal('35') and score.total_score <= Decimal('44'):
                score.grade = 'F'   # GPA: 1.00
            else:
                score.grade = 'Ungraded'  # GPA: 0.00

            # Save the updated score instance
            score.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully recalculated score for {score.student.fullname}'))

        self.stdout.write(self.style.SUCCESS('All scores recalculated successfully!'))
