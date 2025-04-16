# from django.core.management.base import BaseCommand
# from reports.models import Score
# from django.db.models import Max


# class Command(BaseCommand):
#     help = 'Recalculate, update scores for all Score instances in the database, and remove duplicates'
#     def handle(self, *args, **kwargs):
#         # Fetch all Score instances
#         scores = Score.objects.all()

#         # Loop through each score instance to process duplicates
#         for score in scores:
#             self.stdout.write(f'Processing for {score.student.fullname} - {score.subject.name} - Term {score.term.term_name}')

#             # Find other scores for the same student, subject, and term
#             duplicates = Score.objects.filter(
#                 student=score.student,
#                 subject=score.subject,
#                 term=score.term
#             ).exclude(id=score.id)

#             # Delete the duplicate scores (older scores)
#             if duplicates.exists():
#                 self.stdout.write(f'Deleting {duplicates.count()} duplicate(s) for {score.student.fullname} - {score.subject.name}')
#                 duplicates.delete()

#             # Call save to trigger recalculation of the current score
#             score.save()

#             self.stdout.write(self.style.SUCCESS(f'Successfully recalculated and retained the most recent score for {score.student.fullname}'))

#         self.stdout.write(self.style.SUCCESS('All scores recalculated and duplicates removed successfully!'))



from django.core.management.base import BaseCommand
from reports.models import Score
from django.db.models import Max


class Command(BaseCommand):
    help = 'Recalculate and update scores (including grades) for all Score instances in the database, and remove duplicates'

    def handle(self, *args, **kwargs):
        # Fetch all Score instances
        scores = Score.objects.all()

        # Loop through each score instance to process duplicates
        for score in scores:
            self.stdout.write(f'Processing {score.student.fullname} - {score.subject.name} - Term {score.term.term_name}')

            # Find other scores for the same student, subject, and term (excluding current)
            duplicates = Score.objects.filter(
                student=score.student,
                subject=score.subject,
                term=score.term
            ).exclude(id=score.id)

            # Delete duplicate scores
            if duplicates.exists():
                self.stdout.write(f'Deleting {duplicates.count()} duplicate(s) for {score.student.fullname} - {score.subject.name}')
                duplicates.delete()

            # Recalculate score and grade by saving again
            score.save()  # This will auto-trigger grade & total_score calculation from model's save()

            # Optional log to confirm new grade
            self.stdout.write(
                self.style.SUCCESS(
                    f'Recalculated: {score.student.fullname} - {score.subject.name} => Total: {score.total_score}, Grade: {score.grade}'
                )
            )

        self.stdout.write(self.style.SUCCESS('All scores recalculated, grades updated, and duplicates removed successfully!'))
