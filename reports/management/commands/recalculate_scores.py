"""
Django Management Command: Recalculate All Scores and GPAs

This command recalculates all exam scores (applying the 70% calculation),
total scores, grades, and GPAs for all students across all report types.

Usage:
    python manage.py recalculate_scores
    python manage.py recalculate_scores --dry-run  (to preview changes without saving)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from reports.models import (
    Score, AcademicReport, MidtermReport, MockReport,
    ProgressiveTestOneReport, ProgressiveTestTwoReport, Student
)
from reports.utils import calculate_gpa
from decimal import Decimal


class Command(BaseCommand):
    help = 'Recalculates all exam scores (70%), total scores, grades, and GPAs for all students'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without actually saving to database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('=' * 70))
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))
            self.stdout.write(self.style.WARNING('=' * 70))
        else:
            self.stdout.write(self.style.WARNING('=' * 70))
            self.stdout.write(self.style.WARNING('LIVE MODE - All changes will be saved to database'))
            self.stdout.write(self.style.WARNING('=' * 70))

        self.stdout.write('')

        # Statistics
        stats = {
            'scores_updated': 0,
            'academic_reports_updated': 0,
            'midterm_reports_updated': 0,
            'mock_reports_updated': 0,
            'progressive1_reports_updated': 0,
            'progressive2_reports_updated': 0,
            'students_processed': 0,
        }

        try:
            with transaction.atomic():
                # Step 1: Recalculate all Score objects
                self.stdout.write(self.style.HTTP_INFO('Step 1: Recalculating all exam scores and totals...'))
                scores = Score.objects.all().select_related('student', 'subject', 'term')
                total_scores = scores.count()

                for idx, score in enumerate(scores, 1):
                    old_total = score.total_score
                    old_grade = score.grade

                    # Save will trigger the model's save() method which recalculates:
                    # - continuous_assessment (30% of normalized CA)
                    # - total_score (CA + 70% of exam_score)
                    # - grade
                    score.save()

                    stats['scores_updated'] += 1

                    # Show progress every 50 scores
                    if idx % 50 == 0 or idx == total_scores:
                        self.stdout.write(
                            f'  Progress: {idx}/{total_scores} scores processed '
                            f'({(idx/total_scores*100):.1f}%)'
                        )

                self.stdout.write(self.style.SUCCESS(f'✓ Recalculated {stats["scores_updated"]} scores'))
                self.stdout.write('')

                # Step 2: Recalculate Academic Reports (End of Term)
                self.stdout.write(self.style.HTTP_INFO('Step 2: Recalculating Academic Report GPAs (End of Term)...'))
                academic_reports = AcademicReport.objects.all().select_related('student', 'term')

                for report in academic_reports:
                    old_gpa = report.student_gpa

                    # Get scores for this student and term (only assigned subjects)
                    scores = Score.objects.filter(
                        student=report.student,
                        term=report.term,
                        subject__in=report.student.subjects.all()
                    )

                    if scores.exists():
                        # Calculate GPA using the utility function
                        new_gpa = calculate_gpa(scores)
                        report.student_gpa = new_gpa

                        # Update the student_scores many-to-many relationship
                        report.student_scores.set(scores)

                        # Save the report
                        report.save()

                        stats['academic_reports_updated'] += 1

                        if old_gpa != new_gpa:
                            self.stdout.write(
                                f'  Updated: {report.student.fullname} - '
                                f'{report.term.term_name} (GPA: {old_gpa} → {new_gpa})'
                            )

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Updated {stats["academic_reports_updated"]} Academic Reports'
                ))
                self.stdout.write('')

                # Step 3: Recalculate Midterm Reports
                self.stdout.write(self.style.HTTP_INFO('Step 3: Recalculating Midterm Report GPAs...'))
                midterm_reports = MidtermReport.objects.all().select_related('student', 'term')

                for report in midterm_reports:
                    scores = Score.objects.filter(
                        student=report.student,
                        term=report.term,
                        subject__in=report.student.subjects.all()
                    )

                    if scores.exists():
                        # Calculate GPA from midterm scores
                        midterm_scores = [score.midterm_score for score in scores]
                        total_gpa = sum([self._get_gpa_from_score(float(s)) for s in midterm_scores])
                        new_gpa = round(total_gpa / len(midterm_scores), 2) if midterm_scores else 0.0

                        report.midterm_gpa = new_gpa

                        # Update the student_scores many-to-many relationship
                        report.student_scores.set(scores)

                        # Save the report
                        report.save()
                        stats['midterm_reports_updated'] += 1

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Updated {stats["midterm_reports_updated"]} Midterm Reports'
                ))
                self.stdout.write('')

                # Step 4: Recalculate Mock Reports
                self.stdout.write(self.style.HTTP_INFO('Step 4: Recalculating Mock Report GPAs...'))
                mock_reports = MockReport.objects.all().select_related('student', 'term')

                for report in mock_reports:
                    scores = Score.objects.filter(
                        student=report.student,
                        term=report.term,
                        subject__in=report.student.subjects.all()
                    )

                    if scores.exists():
                        # Calculate GPA from mock scores
                        mock_scores = [score.mock_score for score in scores]
                        total_gpa = sum([self._get_gpa_from_score(float(s)) for s in mock_scores])
                        new_gpa = round(total_gpa / len(mock_scores), 2) if mock_scores else 0.0

                        report.mock_gpa = new_gpa

                        # Update the student_scores many-to-many relationship
                        report.student_scores.set(scores)

                        # Save the report
                        report.save()
                        stats['mock_reports_updated'] += 1

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Updated {stats["mock_reports_updated"]} Mock Reports'
                ))
                self.stdout.write('')

                # Step 5: Recalculate Progressive Test 1 Reports
                self.stdout.write(self.style.HTTP_INFO('Step 5: Recalculating Progressive Test 1 GPAs...'))
                prog1_reports = ProgressiveTestOneReport.objects.all().select_related('student', 'term')

                for report in prog1_reports:
                    scores = Score.objects.filter(
                        student=report.student,
                        term=report.term,
                        subject__in=report.student.subjects.all()
                    )

                    if scores.exists():
                        # Calculate GPA from progressive test 1 scores
                        prog_scores = [score.progressive_test_1_score for score in scores]
                        total_gpa = sum([self._get_gpa_from_score(float(s)) for s in prog_scores])
                        new_gpa = round(total_gpa / len(prog_scores), 2) if prog_scores else 0.0

                        report.progressive_test1_gpa = new_gpa

                        # Update the student_scores many-to-many relationship
                        report.student_scores.set(scores)

                        # Save the report
                        report.save()
                        stats['progressive1_reports_updated'] += 1

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Updated {stats["progressive1_reports_updated"]} Progressive Test 1 Reports'
                ))
                self.stdout.write('')

                # Step 6: Recalculate Progressive Test 2 Reports
                self.stdout.write(self.style.HTTP_INFO('Step 6: Recalculating Progressive Test 2 GPAs...'))
                prog2_reports = ProgressiveTestTwoReport.objects.all().select_related('student', 'term')

                for report in prog2_reports:
                    scores = Score.objects.filter(
                        student=report.student,
                        term=report.term,
                        subject__in=report.student.subjects.all()
                    )

                    if scores.exists():
                        # Calculate GPA from progressive test 2 scores
                        prog_scores = [score.progressive_test_2_score for score in scores]
                        total_gpa = sum([self._get_gpa_from_score(float(s)) for s in prog_scores])
                        new_gpa = round(total_gpa / len(prog_scores), 2) if prog_scores else 0.0

                        report.progressive_test2_gpa = new_gpa

                        # Update the student_scores many-to-many relationship
                        report.student_scores.set(scores)

                        # Save the report
                        report.save()
                        stats['progressive2_reports_updated'] += 1

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Updated {stats["progressive2_reports_updated"]} Progressive Test 2 Reports'
                ))
                self.stdout.write('')

                # Get total students processed
                stats['students_processed'] = Student.objects.count()

                # If dry run, rollback the transaction
                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING(''))
                    self.stdout.write(self.style.WARNING('DRY RUN: All changes rolled back (not saved)'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error occurred: {str(e)}'))
            raise

        # Print summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('RECALCULATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write(f'Total Students in System: {stats["students_processed"]}')
        self.stdout.write(f'Individual Scores Recalculated: {stats["scores_updated"]}')
        self.stdout.write(f'Academic Reports (End of Term) Updated: {stats["academic_reports_updated"]}')
        self.stdout.write(f'Midterm Reports Updated: {stats["midterm_reports_updated"]}')
        self.stdout.write(f'Mock Reports Updated: {stats["mock_reports_updated"]}')
        self.stdout.write(f'Progressive Test 1 Reports Updated: {stats["progressive1_reports_updated"]}')
        self.stdout.write(f'Progressive Test 2 Reports Updated: {stats["progressive2_reports_updated"]}')
        self.stdout.write('')

        if not dry_run:
            self.stdout.write(self.style.SUCCESS('All changes have been saved to the database!'))
        else:
            self.stdout.write(self.style.WARNING('No changes were saved (DRY RUN mode)'))
            self.stdout.write(self.style.WARNING('Run without --dry-run flag to save changes'))

        self.stdout.write('')

    def _get_gpa_from_score(self, score):
        """
        Convert a score (0-100) to GPA (0.00-4.00) based on grading scale
        """
        if score >= 95:
            return 4.00
        elif score >= 80:
            return 3.67
        elif score >= 75:
            return 3.33
        elif score >= 70:
            return 3.00
        elif score >= 65:
            return 2.67
        elif score >= 60:
            return 2.33
        elif score >= 50:
            return 2.00
        elif score >= 45:
            return 1.67
        elif score >= 35:
            return 1.00
        else:
            return 0.00
