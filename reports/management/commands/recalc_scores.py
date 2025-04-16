from django.core.management.base import BaseCommand
from reports.models import Score
from django.db.models import Count
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


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

        # Step 2: Assign grades based on total_score
        scores = Score.objects.all()

        for score in scores:
            original_grade = score.grade

            if score.total_score is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️ Skipping score with missing total_score for {score.student.fullname} - {score.subject.name}"
                    )
                )
                continue

            try:
                # Convert total_score to Decimal explicitly
                total_score_decimal = Decimal(str(score.total_score))
                # Round to nearest whole number using ROUND_HALF_UP
                rounded_score = total_score_decimal.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                # Clamp between 0 and 100
                rounded_score = max(Decimal(0), min(Decimal(100), rounded_score))
            except (InvalidOperation, TypeError, ValueError) as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Invalid total_score '{score.total_score}' for {score.student.fullname} - {score.subject.name}: {e}"
                    )
                )
                continue

            # Assign grade based on rounded score
            score.grade = self.assign_grade(rounded_score)

            score.save(update_fields=['grade'])

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ {score.student.fullname} - {score.subject.name} => Score: {rounded_score}, Grade: {score.grade} (was: {original_grade})"
                )
            )

        self.stdout.write(self.style.SUCCESS("🎓 All scores graded successfully, and duplicates removed."))

    def assign_grade(self, score: Decimal) -> str:
        if 95 <= score <= 100:
            return 'A*'
        elif 80 <= score <= 94:
            return 'A'
        elif 75 <= score <= 79:
            return 'B+'
        elif 70 <= score <= 74:
            return 'B'
        elif 65 <= score <= 69:
            return 'C+'
        elif 60 <= score <= 64:
            return 'C'
        elif 50 <= score <= 59:
            return 'D'
        elif 45 <= score <= 49:
            return 'E'
        elif 35 <= score <= 44:
            return 'F'
        else:
            return 'Ungraded'
