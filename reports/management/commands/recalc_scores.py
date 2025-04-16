# from django.core.management.base import BaseCommand
# from reports.models import Score
# from django.db.models import Max


# class Command(BaseCommand):
#     help = 'Recalculate and update scores (including grades) for all Score instances in the database, and remove duplicates'

#     def handle(self, *args, **kwargs):
#         # Fetch all Score instances
#         scores = Score.objects.all()

#         # Loop through each score instance to process duplicates
#         for score in scores:
#             self.stdout.write(f'Processing {score.student.fullname} - {score.subject.name} - Term {score.term.term_name}')

#             # Find other scores for the same student, subject, and term (excluding current)
#             duplicates = Score.objects.filter(
#                 student=score.student,
#                 subject=score.subject,
#                 term=score.term
#             ).exclude(id=score.id)

#             # Delete duplicate scores
#             if duplicates.exists():
#                 self.stdout.write(f'Deleting {duplicates.count()} duplicate(s) for {score.student.fullname} - {score.subject.name}')
#                 duplicates.delete()

#             # Recalculate score and grade by saving again
#             score.save()  # This will auto-trigger grade & total_score calculation from model's save()

#             # Optional log to confirm new grade
#             self.stdout.write(
#                 self.style.SUCCESS(
#                     f'Recalculated: {score.student.fullname} - {score.subject.name} => Total: {score.total_score}, Grade: {score.grade}'
#                 )
#             )

#         self.stdout.write(self.style.SUCCESS('All scores recalculated, grades updated, and duplicates removed successfully!'))





from django.core.management.base import BaseCommand
from reports.models import Score
from django.db.models import Count
from decimal import Decimal, ROUND_HALF_UP


class Command(BaseCommand):
    help = 'Update grades for all Score instances based on existing total_score and remove duplicates.'

    def handle(self, *args, **kwargs):
        # Step 1: Remove duplicates
        duplicates = (
            Score.objects.values('student', 'subject', 'term')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        for dup in duplicates:
            scores = Score.objects.filter(
                student=dup['student'],
                subject=dup['subject'],
                term=dup['term']
            ).order_by('-created_at')

            to_delete = scores[1:]
            if to_delete.exists():
                self.stdout.write(
                    f"Deleting {to_delete.count()} duplicate(s) for student={dup['student']}, subject={dup['subject']}, term={dup['term']}"
                )
                to_delete.delete()

        # Step 2: Assign grades based on existing total_score
        scores = Score.objects.all()

        for score in scores:
            original_grade = score.grade

            # Round total score to nearest whole number for grading
            rounded_score = score.total_score.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            # Assign grade based on rounded score
            if rounded_score >= 95:
                score.grade = 'A*'
            elif rounded_score >= 80:
                score.grade = 'A'
            elif rounded_score >= 75:
                score.grade = 'B+'
            elif rounded_score >= 70:
                score.grade = 'B'
            elif rounded_score >= 65:
                score.grade = 'C+'
            elif rounded_score >= 60:
                score.grade = 'C'
            elif rounded_score >= 50:
                score.grade = 'D'
            elif rounded_score >= 45:
                score.grade = 'E'
            elif rounded_score >= 35:
                score.grade = 'F'
            else:
                score.grade = 'Ungraded'

            score.save(update_fields=['grade'])  # only update the grade field

            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated Grade: {score.student.fullname} - {score.subject.name} => Score: {rounded_score}, Grade: {score.grade} (was: {original_grade})"
                )
            )

        self.stdout.write(self.style.SUCCESS("✅ Grades updated based on total_score, and duplicates removed."))
