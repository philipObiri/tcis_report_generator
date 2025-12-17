from django.core.management.base import BaseCommand
from decimal import Decimal
from reports.models import Score


class Command(BaseCommand):
    help = 'Assign correct grades to all scores based on total_score'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually updating records',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))

        self.stdout.write(self.style.WARNING('Starting grade assignment...'))

        # Get all scores
        scores = Score.objects.all()
        total_count = scores.count()
        updated_count = 0
        unchanged_count = 0

        self.stdout.write(f'Processing {total_count} score records...\n')

        for score in scores:
            # Calculate what the grade should be based on total_score
            correct_grade = self.calculate_grade(score.total_score)

            # Check if grade needs updating
            if score.grade != correct_grade:
                old_grade = score.grade

                if not dry_run:
                    score.grade = correct_grade
                    # Use update_fields to avoid triggering full save logic
                    score.save(update_fields=['grade'])

                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  [UPDATED] {score.student.fullname} - {score.subject.name} - '
                        f'{score.term.term_name}: {old_grade} -> {correct_grade} '
                        f'(Total: {score.total_score})'
                    )
                )
            else:
                unchanged_count += 1

        # Summary
        self.stdout.write('\n' + '='*80)
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[DRY RUN COMPLETE]\n'
                    f'Total records: {total_count}\n'
                    f'Would be updated: {updated_count}\n'
                    f'Already correct: {unchanged_count}\n'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[SUCCESS] Grade assignment complete!\n'
                    f'Total records: {total_count}\n'
                    f'Updated: {updated_count}\n'
                    f'Unchanged: {unchanged_count}\n'
                )
            )

    def calculate_grade(self, total_score):
        """Calculate grade based on total_score using the same logic as Score.save()"""
        if Decimal('95') <= total_score <= Decimal('100'):
            return 'A*'
        elif Decimal('80') <= total_score <= Decimal('94'):
            return 'A'
        elif Decimal('75') <= total_score <= Decimal('79'):
            return 'B+'
        elif Decimal('70') <= total_score <= Decimal('74'):
            return 'B'
        elif Decimal('65') <= total_score <= Decimal('69'):
            return 'C+'
        elif Decimal('60') <= total_score <= Decimal('64'):
            return 'C'
        elif Decimal('50') <= total_score <= Decimal('59'):
            return 'D'
        elif Decimal('45') <= total_score <= Decimal('49'):
            return 'E'
        elif Decimal('35') <= total_score <= Decimal('44'):
            return 'F'
        else:
            return 'Ungraded'
