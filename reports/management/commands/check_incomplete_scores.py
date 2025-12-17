from django.core.management.base import BaseCommand
from decimal import Decimal
from reports.models import Score, Subject
from collections import defaultdict


class Command(BaseCommand):
    help = 'Check for incomplete scores (exam entered but missing component scores for CA calculation)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--term',
            type=str,
            help='Filter by specific term name',
        )
        parser.add_argument(
            '--class-year',
            type=str,
            help='Filter by specific class year',
        )
        parser.add_argument(
            '--export',
            type=str,
            help='Export results to CSV file',
        )

    def handle(self, *args, **options):
        term_filter = options.get('term')
        class_year_filter = options.get('class_year')
        export_file = options.get('export')

        self.stdout.write(self.style.WARNING('Checking for incomplete scores...'))

        # Build query: scores with exam but no CA (meaning component scores missing)
        queryset = Score.objects.filter(
            exam_score__gt=0,
            continuous_assessment=0
        ).select_related('student', 'subject', 'term', 'student__class_year')

        if term_filter:
            queryset = queryset.filter(term__term_name__icontains=term_filter)
            self.stdout.write(f'Filtering for term: {term_filter}')

        if class_year_filter:
            queryset = queryset.filter(student__class_year__name__icontains=class_year_filter)
            self.stdout.write(f'Filtering for class year: {class_year_filter}')

        incomplete_scores = queryset.order_by('student__fullname', 'subject__name')
        total_count = incomplete_scores.count()

        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('\n[SUCCESS] No incomplete scores found! All scores have proper CA values.'))
            return

        # Group by student and term for better reporting
        grouped = defaultdict(lambda: defaultdict(list))
        for score in incomplete_scores:
            grouped[score.student.fullname][score.term.term_name].append(score)

        self.stdout.write(self.style.ERROR(f'\n[FOUND] {total_count} incomplete scores'))
        self.stdout.write('='*100)

        # Prepare export data if needed
        export_data = []
        if export_file:
            export_data.append(['Student', 'Class Year', 'Term', 'Subject', 'Grading System', 'Exam Score', 'CA Score',
                               'Classwork', 'PT1', 'PT2', 'Midterm', 'Status'])

        # Display results
        for student_name in sorted(grouped.keys()):
            self.stdout.write(f'\n{self.style.WARNING(student_name)}')
            for term_name, scores in grouped[student_name].items():
                self.stdout.write(f'  Term: {term_name}')
                for score in scores:
                    grading_system = "Cambridge" if score.subject.grading_system == Subject.CAMBRIDGE else "Standard"
                    class_year = score.student.class_year.name if score.student.class_year else 'N/A'

                    # Check which component scores are missing
                    missing_components = []
                    if score.class_work_score == 0:
                        missing_components.append('Classwork')
                    if score.progressive_test_1_score == 0:
                        missing_components.append('PT1')
                    if score.progressive_test_2_score == 0:
                        missing_components.append('PT2')
                    if score.midterm_score == 0:
                        missing_components.append('Midterm')

                    status = f"Missing: {', '.join(missing_components)}"

                    self.stdout.write(
                        f'    - {score.subject.name} ({grading_system}): '
                        f'Exam={float(score.exam_score):.2f}, CA={float(score.continuous_assessment):.2f} | '
                        f'{self.style.ERROR(status)}'
                    )

                    # Add to export data
                    if export_file:
                        export_data.append([
                            student_name,
                            class_year,
                            term_name,
                            score.subject.name,
                            grading_system,
                            f'{float(score.exam_score):.2f}',
                            f'{float(score.continuous_assessment):.2f}',
                            f'{float(score.class_work_score):.2f}',
                            f'{float(score.progressive_test_1_score):.2f}',
                            f'{float(score.progressive_test_2_score):.2f}',
                            f'{float(score.midterm_score):.2f}',
                            status
                        ])

        # Summary by term
        self.stdout.write('\n' + '='*100)
        self.stdout.write(self.style.WARNING('\nSUMMARY BY TERM:'))
        term_counts = defaultdict(int)
        for score in incomplete_scores:
            term_counts[score.term.term_name] += 1

        for term, count in sorted(term_counts.items()):
            self.stdout.write(f'  {term}: {count} incomplete scores')

        # Summary by subject
        self.stdout.write(self.style.WARNING('\nSUMMARY BY SUBJECT:'))
        subject_counts = defaultdict(int)
        for score in incomplete_scores:
            subject_counts[score.subject.name] += 1

        for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True):
            self.stdout.write(f'  {subject}: {count} incomplete scores')

        # Export to CSV if requested
        if export_file:
            import csv
            try:
                with open(export_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(export_data)
                self.stdout.write(self.style.SUCCESS(f'\n[EXPORTED] Results saved to {export_file}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\n[ERROR] Failed to export: {str(e)}'))

        self.stdout.write('\n' + '='*100)
        self.stdout.write(
            self.style.ERROR(
                f'\n[ACTION REQUIRED] {total_count} scores need component scores entered.\n'
                'Teachers need to enter: Classwork, Progressive Test 1, Progressive Test 2, and Midterm scores.\n'
                'These component scores are required to calculate the 30% Continuous Assessment.\n'
            )
        )
