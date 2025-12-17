from django.core.management.base import BaseCommand
from decimal import Decimal
from reports.models import Score, Subject


class Command(BaseCommand):
    help = 'Recalculate continuous assessment for all scores by resaving them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually updating records',
        )
        parser.add_argument(
            '--student',
            type=str,
            help='Only recalculate for specific student (by fullname)',
        )
        parser.add_argument(
            '--subject',
            type=str,
            help='Only recalculate for specific subject (by name)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        student_filter = options.get('student')
        subject_filter = options.get('subject')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))

        self.stdout.write(self.style.WARNING('Starting continuous assessment recalculation...'))

        # Build query
        queryset = Score.objects.all()

        if student_filter:
            queryset = queryset.filter(student__fullname__icontains=student_filter)
            self.stdout.write(f'Filtering for student: {student_filter}')

        if subject_filter:
            queryset = queryset.filter(subject__name__icontains=subject_filter)
            self.stdout.write(f'Filtering for subject: {subject_filter}')

        # Select related to avoid N+1 queries
        scores = queryset.select_related('student', 'subject', 'term')
        total_count = scores.count()
        updated_count = 0
        zero_ca_count = 0
        error_count = 0

        self.stdout.write(f'Processing {total_count} score records...\n')

        for score in scores:
            old_ca = score.continuous_assessment
            old_total = score.total_score
            old_grade = score.grade

            # Check if this score has any component scores
            has_components = any([
                score.class_work_score != 0,
                score.progressive_test_1_score != 0,
                score.progressive_test_2_score != 0,
                score.midterm_score != 0
            ])

            try:
                if not dry_run:
                    # Resave to trigger CA recalculation
                    score.save()

                # Check if CA changed
                new_ca = score.continuous_assessment
                new_total = score.total_score
                new_grade = score.grade

                if old_ca != new_ca or old_total != new_total or old_grade != new_grade:
                    updated_count += 1

                    grading_system = "Cambridge" if score.subject.grading_system == Subject.CAMBRIDGE else "Standard"

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  [UPDATED] {score.student.fullname} - {score.subject.name} ({grading_system}) - {score.term.term_name}\n'
                            f'    CA: {float(old_ca):.2f} -> {float(new_ca):.2f}\n'
                            f'    Total: {float(old_total):.2f} -> {float(new_total):.2f}\n'
                            f'    Grade: {old_grade} -> {new_grade}\n'
                            f'    Components: CW={float(score.class_work_score):.2f}, PT1={float(score.progressive_test_1_score):.2f}, '
                            f'PT2={float(score.progressive_test_2_score):.2f}, Mid={float(score.midterm_score):.2f}, Exam={float(score.exam_score):.2f}'
                        )
                    )

                # Track scores with 0 CA after recalculation
                if new_ca == 0 and has_components:
                    zero_ca_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'  [WARNING] {score.student.fullname} - {score.subject.name}: CA is 0 but has component scores!'
                        )
                    )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'  [ERROR] Failed to update {score.student.fullname} - {score.subject.name}: {str(e)}'
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
                    f'Scores with 0 CA despite having components: {zero_ca_count}\n'
                    f'Errors: {error_count}\n'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[SUCCESS] Continuous assessment recalculation complete!\n'
                    f'Total records: {total_count}\n'
                    f'Updated: {updated_count}\n'
                    f'Unchanged: {total_count - updated_count - error_count}\n'
                    f'Scores with 0 CA despite having components: {zero_ca_count}\n'
                    f'Errors: {error_count}\n'
                )
            )
