from django.core.management.base import BaseCommand
from decimal import Decimal
from reports.models import Score


class Command(BaseCommand):
    help = 'Recalculate CA, total scores, and grades for all score records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually updating records',
        )
        parser.add_argument(
            '--ungraded-only',
            action='store_true',
            help='Only process scores with grade = "Ungraded"',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        ungraded_only = options['ungraded_only']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))

        self.stdout.write(self.style.WARNING('Starting grade recalculation...'))

        # Get scores to process
        if ungraded_only:
            scores = Score.objects.filter(grade='Ungraded')
            self.stdout.write(f'Processing only UNGRADED scores...\n')
        else:
            scores = Score.objects.all()
            self.stdout.write(f'Processing ALL scores...\n')

        total_count = scores.count()
        updated_count = 0
        unchanged_count = 0
        error_count = 0

        self.stdout.write(f'Found {total_count} score records to process...\n')

        for score in scores:
            try:
                # Store old values
                old_ca = score.continuous_assessment
                old_total = score.total_score
                old_grade = score.grade

                if dry_run:
                    # Calculate what values would be without saving
                    grading_system = score.subject.grading_system if score.subject else 'S'

                    # Calculate CA based on grading system
                    if grading_system == 'C':  # Cambridge
                        new_ca = (
                            (score.class_work_score * Decimal('0.0375')) +
                            (score.progressive_test_1_score * Decimal('0.075')) +
                            (score.progressive_test_2_score * Decimal('0.075')) +
                            (score.midterm_score * Decimal('0.1125'))
                        ).quantize(Decimal('0.01'))
                    else:  # Standard
                        total_ca_score = (
                            score.class_work_score +
                            score.progressive_test_1_score +
                            score.progressive_test_2_score +
                            score.midterm_score
                        )
                        normalized_ca = (total_ca_score / Decimal('400')) * Decimal('100')
                        new_ca = (normalized_ca * Decimal('0.30')).quantize(Decimal('0.01'))

                    # Calculate total score
                    new_total = (new_ca + (score.exam_score * Decimal('0.70'))).quantize(Decimal('0.01'))

                    # Calculate grade
                    if Decimal('95') <= new_total <= Decimal('100'):
                        new_grade = 'A*'
                    elif Decimal('80') <= new_total < Decimal('95'):
                        new_grade = 'A'
                    elif Decimal('75') <= new_total < Decimal('80'):
                        new_grade = 'B+'
                    elif Decimal('70') <= new_total < Decimal('75'):
                        new_grade = 'B'
                    elif Decimal('65') <= new_total < Decimal('70'):
                        new_grade = 'C+'
                    elif Decimal('60') <= new_total < Decimal('65'):
                        new_grade = 'C'
                    elif Decimal('50') <= new_total < Decimal('60'):
                        new_grade = 'D'
                    elif Decimal('45') <= new_total < Decimal('50'):
                        new_grade = 'E'
                    elif Decimal('35') <= new_total < Decimal('45'):
                        new_grade = 'F'
                    else:
                        new_grade = 'Ungraded'
                else:
                    # Actually save to trigger recalculation
                    score.save()
                    new_ca = score.continuous_assessment
                    new_total = score.total_score
                    new_grade = score.grade

                # Check if anything changed
                if old_ca != new_ca or old_total != new_total or old_grade != new_grade:
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  [UPDATED] {score.student.fullname} - {score.subject.name} - {score.term.term_name}\n'
                            f'    CA: {old_ca} -> {new_ca}\n'
                            f'    Total: {old_total} -> {new_total}\n'
                            f'    Grade: {old_grade} -> {new_grade}'
                        )
                    )
                else:
                    unchanged_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'  [ERROR] {score.student.fullname} - {score.subject.name} - {score.term.term_name}: {str(e)}'
                    )
                )

        # Summary
        self.stdout.write('\n' + '='*80)
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[DRY RUN COMPLETE]\n'
                    f'Total records: {total_count}\n'
                    f'Would be updated: {updated_count}\n'
                    f'Already correct: {unchanged_count}\n'
                    f'Errors: {error_count}\n'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[SUCCESS] Grade recalculation complete!\n'
                    f'Total records: {total_count}\n'
                    f'Updated: {updated_count}\n'
                    f'Unchanged: {unchanged_count}\n'
                    f'Errors: {error_count}\n'
                )
            )
