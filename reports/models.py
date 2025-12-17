from django.db import models
from django.contrib.auth.models import User  
from decimal import Decimal,ROUND_HALF_UP
from django.core.exceptions import ValidationError
from reports.utils import calculate_gpa

class Level(models.Model):
    LOWER = 'Lower Secondary'
    UPPER = 'Upper Secondary'
    SIXTH_FORM = 'Sixth Form'

    LEVEL_CHOICES = [
        (LOWER, 'Lower Secondary'),
        (UPPER, 'Upper Secondary'),
        (SIXTH_FORM, 'Sixth Form'),
    ]
    
    name = models.CharField(max_length=100, choices=LEVEL_CHOICES)

    def __str__(self):
        return self.name

class ClassYear(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='level')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Class / Year'
        verbose_name_plural = 'Classes / Years'

    def __str__(self):
        return f"{self.level.name} - {self.name}"

class Term(models.Model):
    TERM_1 = 'Term 1'
    TERM_2 = 'Term 2'
    TERM_3 = 'Term 3'

    TERM_CHOICES = [
        (TERM_1, 'Term 1'),
        (TERM_2, 'Term 2'),
        (TERM_3, 'Term 3'),
    ]
    
    term_name = models.CharField(max_length=100, choices=TERM_CHOICES)
    class_year = models.ForeignKey(ClassYear, on_delete=models.CASCADE, related_name='term')
    
    def __str__(self):
        return f"{self.term_name} - {self.class_year.name}"

class Subject(models.Model):
    STANDARD = 'standard'
    CAMBRIDGE = 'cambridge'

    GRADING_SYSTEM_CHOICES = [
        (STANDARD, 'Standard Grading System'),
        (CAMBRIDGE, 'Cambridge Grading System'),
    ]

    name = models.CharField(max_length=100)
    class_year = models.ManyToManyField(ClassYear, related_name='subjects')
    grading_system = models.CharField(
        max_length=20,
        choices=GRADING_SYSTEM_CHOICES,
        default=STANDARD,
        help_text='Select the grading system for this subject'
    )

    def __str__(self):
        return self.name

class Student(models.Model):
    fullname = models.CharField(max_length=255)
    class_year = models.ForeignKey(ClassYear, on_delete=models.CASCADE, related_name='students')
    subjects = models.ManyToManyField(Subject, related_name='students', blank=True)

    def __str__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)

        if created or self._state.fields_cache.get('class_year') != self.class_year:
            self.subjects.set(self.class_year.subjects.all())

        self.save_m2m()

    def save_m2m(self):
        if self.pk:
            self.subjects.clear()
            self.subjects.add(*self.class_year.subjects.all())


class StudentReportComment(models.Model):
    """
    Store student report comments separately from scores.
    Comments are tied to student + class_year + term, completely independent of scores.
    This ensures comments are consistent across all subjects for a student in a specific class and term.
    """
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='report_comments')
    class_year = models.ForeignKey('ClassYear', on_delete=models.CASCADE, related_name='report_comments', null=True)
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name='report_comments')
    academic_comment = models.TextField(blank=True, default='')
    behavioral_comment = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'class_year', 'term')
        verbose_name = 'Student Report Comment'
        verbose_name_plural = 'Student Report Comments'

    def __str__(self):
        class_year_name = self.class_year.name if self.class_year else 'No Class'
        return f"Comments for {self.student.fullname} - {class_year_name} - {self.term.term_name}"


class MockReportComment(models.Model):
    """
    Store mock report comments separately from scores.
    Comments are tied to student + class_year + term, completely independent of scores.
    This ensures comments are consistent across all subjects for a student's mock report.
    """
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='mock_report_comments')
    class_year = models.ForeignKey('ClassYear', on_delete=models.CASCADE, related_name='mock_report_comments')
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name='mock_report_comments')
    academic_comment = models.TextField(blank=True, default='')
    behavioral_comment = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'class_year', 'term')
        verbose_name = 'Mock Report Comment'
        verbose_name_plural = 'Mock Report Comments'

    def __str__(self):
        class_year_name = self.class_year.name if self.class_year else 'No Class'
        return f"Mock Comments for {self.student.fullname} - {class_year_name} - {self.term.term_name}"


class Score(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='scores')
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name='scores')
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name='scores')

    # Individual scores
    class_work_score = models.DecimalField(max_digits=100, decimal_places=2, default=Decimal('0.0'))
    progressive_test_1_score = models.DecimalField(max_digits=100, decimal_places=2, default=Decimal('0.0'))
    progressive_test_2_score = models.DecimalField(max_digits=100, decimal_places=2, default=Decimal('0.0'))
    progressive_test_3_score = models.DecimalField(max_digits=100, decimal_places=2, default=Decimal('0.0'))
    midterm_score = models.DecimalField(max_digits=100, decimal_places=2, default=Decimal('0.0'))
    mock_score = models.DecimalField(max_digits=100, decimal_places=2, default=Decimal('0.0'))

    # Exam score (main exam at the end of the term)
    exam_score = models.DecimalField(max_digits=100, decimal_places=2, default=Decimal('0.0'))

    continuous_assessment = models.DecimalField(max_digits=25, decimal_places=2, default=Decimal('0.0'))
    total_score = models.DecimalField(max_digits=100, decimal_places=2, default=Decimal('0.0'))
    grade = models.CharField(max_length=255, blank=True)

    # Comments (only for exam scores / end of term reports)
    academic_comment = models.TextField(blank=True, null=True, help_text='Academic comment by head class teacher')
    behavioral_comment = models.TextField(blank=True, null=True, help_text='Behavioral comment by head class teacher')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        # Add unique constraint to prevent duplicates
        unique_together = ['student', 'subject', 'term', 'created_by']

    def save(self, *args, **kwargs):
        # Check the subject's grading system
        grading_system = self.subject.grading_system if self.subject else Subject.STANDARD

        if grading_system == Subject.CAMBRIDGE:
            # Cambridge Grading System with Progressive Test 2 included
            # Weights scaled to total 30% CA:
            # - Classwork & Homework: 3.75% (originally 5%, scaled by 0.75)
            # - Progressive Test 1: 7.5% (originally 10%, scaled by 0.75)
            # - Progressive Test 2: 7.5% (originally 10%, scaled by 0.75)
            # - Midterm: 11.25% (originally 15%, scaled by 0.75)
            # Total CA: 30%

            ca_raw = (
                (self.class_work_score * Decimal('0.0375')) +      # 3.75%
                (self.progressive_test_1_score * Decimal('0.075')) + # 7.5%
                (self.progressive_test_2_score * Decimal('0.075')) + # 7.5%
                (self.midterm_score * Decimal('0.1125'))            # 11.25%
            )
            # Round CA to 2 decimal places
            self.continuous_assessment = ca_raw.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            # Standard Grading System
            # Calculate the sum of all the component scores (now out of 400)
            total_continuous_assessment_score = (
                self.class_work_score +
                self.progressive_test_1_score +
                self.progressive_test_2_score +
                self.midterm_score
            )

            # Normalize continuous_assessment to a 100% scale (total is now out of 400)
            normalized_continuous_assessment = (total_continuous_assessment_score / Decimal('400')) * Decimal('100')

            # Calculate Continuous Assessment as 30% of normalized value
            ca_raw = normalized_continuous_assessment * Decimal('0.30')

            # Round CA to 2 decimal places
            self.continuous_assessment = ca_raw.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Calculate Total Score: 30% of CA + 70% of exam
        raw_total_score = self.continuous_assessment + (self.exam_score * Decimal('0.70'))

        # Round total_score to 2 decimal places
        self.total_score = raw_total_score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Assign grade based on rounded total_score
        if Decimal('95') <= self.total_score <= Decimal('100'):
            self.grade = 'A*'
        elif Decimal('80') <= self.total_score < Decimal('95'):
            self.grade = 'A'
        elif Decimal('75') <= self.total_score < Decimal('80'):
            self.grade = 'B+'
        elif Decimal('70') <= self.total_score < Decimal('75'):
            self.grade = 'B'
        elif Decimal('65') <= self.total_score < Decimal('70'):
            self.grade = 'C+'
        elif Decimal('60') <= self.total_score < Decimal('65'):
            self.grade = 'C'
        elif Decimal('50') <= self.total_score < Decimal('60'):
            self.grade = 'D'
        elif Decimal('45') <= self.total_score < Decimal('50'):
            self.grade = 'E'
        elif Decimal('35') <= self.total_score < Decimal('45'):
            self.grade = 'F'
        else:
            self.grade = 'Ungraded'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.fullname} - {self.subject.name} - {self.total_score}"


class MidtermReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='midterm_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='midterm_reports')

    # Midterm GPA (calculated directly from the midterm_score field)
    midterm_gpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Linking related scores to the report (many-to-many relationship with Score)
    student_scores = models.ManyToManyField(Score, related_name='midterm_reports')

    # User who generated the report
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_midterm_reports')


    comment = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Midterm Report"
        verbose_name_plural = "Midterm Reports"

    def save(self, *args, **kwargs):
        # Ensure the user who generated the report is set automatically
        if not self.generated_by and 'user' in kwargs:
            self.generated_by = kwargs.pop('user', None)

        # Fetch the scores for the student in the current term
        scores = Score.objects.filter(student=self.student, term=self.term)


        # # Calculate GPA using the external calculate_gpa function (from utilities)
        # gpa = calculate_gpa(scores)

        # # Set the calculated GPA
        # self.midterm_gpa = gpa

        # Save the report first to generate an ID
        super().save(*args, **kwargs)

        # Now link the scores to the report (many-to-many relationship)
        self.student_scores.set(scores)  # Many-to-many relationship with Scores: midterm values

        # Save the many-to-many relationship, but don't call save() on the object itself again.
        # This is handled automatically by Django when you call 'set()' on a Many-to-Many field.
        # Just calling self.save() again will ensure everything is persisted.

    def __str__(self):
        return f"Midterm Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.midterm_gpa}"


class MockReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mock_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='mock_reports')

    # Midterm GPA (calculated directly from the midterm_score field)
    mock_gpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Linking related scores to the report (many-to-many relationship with Score)
    student_scores = models.ManyToManyField(Score, related_name='mock_reports')

    # User who generated the report
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_mock_reports')


    comment = models.TextField(blank=True, null=True)


    class Meta:
        verbose_name = "Mock Report"
        verbose_name_plural = "Mock Reports"

    def save(self, *args, **kwargs):
        # Ensure the user who generated the report is set automatically
        if not self.generated_by and 'user' in kwargs:
            self.generated_by = kwargs.pop('user', None)

        # Fetch the scores for the student in the current term
        scores = Score.objects.filter(student=self.student, term=self.term)

        # Save the report first to generate an ID
        super().save(*args, **kwargs)

        # Now link the scores to the report (many-to-many relationship)
        self.student_scores.set(scores)  # Many-to-many relationship with Scores: midterm values

        # Save the many-to-many relationship, but don't call save() on the object itself again.
        # This is handled automatically by Django when you call 'set()' on a Many-to-Many field.
        # Just calling self.save() again will ensure everything is persisted.

    def __str__(self):
        return f"Mock Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.mock_gpa}"


class ProgressiveTestOneReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progressive_test1_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='progressive_test1_reports')

    # Progressive Test 1 GPA (calculated directly from the progressive_test_1_score field)
    progressive_test1_gpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Linking related scores to the report (many-to-many relationship with Score)
    student_scores = models.ManyToManyField(Score, related_name='progressive_test1_reports')

    # User who generated the report
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_progressive_test1_reports')


    comment = models.TextField(blank=True, null=True)


    class Meta:
        verbose_name = "Progressive One Report "
        verbose_name_plural = "Progressive One Reports"

    def save(self, *args, **kwargs):
        # Ensure the user who generated the report is set automatically
        if not self.generated_by and 'user' in kwargs:
            self.generated_by = kwargs.pop('user', None)

        # Fetch the scores for the student in the current term
        scores = Score.objects.filter(student=self.student, term=self.term)

        # Fetch the progressive test score one for each score:
        total_scores = [score.progressive_test_1_score for score in scores]

        # Calculate GPA using the external calculate_gpa function (assuming you have a `calculate_gpa` function)
        gpa = calculate_gpa(total_scores)

        # Set the progressive_test1_gpa based on the calculated GPA
        self.progressive_test1_gpa = gpa

        # Save the report first to generate the ID (this is needed for the ManyToManyField)
        super().save(*args, **kwargs)

        # Now link the scores to the report (many-to-many relationship)
        self.student_scores.set(scores)  # Many-to-many relationship with Scores: progressive test scores

        # Save the many-to-many relationship. Django will handle the saving process automatically when you call 'set()'.
        # Just calling self.save() again will ensure everything is persisted.

    def __str__(self):
        return f"Progressive Test 1 Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.progressive_test1_gpa}"


class ProgressiveTestTwoReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progressive_test2_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='progressive_test2_reports')

    # Progressive Test 2 GPA (calculated directly from the progressive_test_2_score field)
    progressive_test2_gpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Linking related scores to the report (many-to-many relationship with Score)
    student_scores = models.ManyToManyField(Score, related_name='progressive_test2_reports')

    # User who generated the report
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_progressive_test2_reports')
    
    comment = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Progressive Two Report"
        verbose_name_plural = "Progressive Two Reports"

    def save(self, *args, **kwargs):
        # Ensure the user who generated the report is set automatically
        if not self.generated_by and 'user' in kwargs:
            self.generated_by = kwargs.pop('user', None)

        # Get the scores for the student in the current term
        scores = Score.objects.filter(student=self.student, term=self.term)

        # Fetch the progressive test score two for each score:
        total_scores = [score.progressive_test_2_score for score in scores]

        # Calculate GPA using the external calculate_gpa function (assuming you have a `calculate_gpa` function)
        gpa = calculate_gpa(total_scores)

        # Set the progressive_test2_gpa based on the calculated GPA
        self.progressive_test2_gpa = gpa

        # Save the report first to generate an ID (needed for Many-to-Many relationship)
        super().save(*args, **kwargs)

        # Now link the scores to the report (many-to-many relationship)
        self.student_scores.set(scores)  # Many-to-many relationship with Scores: progressive test scores

        # Save the many-to-many relationship. Django will handle this automatically when you call 'set()'.
        # Just calling self.save() again will ensure everything is persisted.

    def __str__(self):
        return f"Progressive Test 2 Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.progressive_test2_gpa}"


class AcademicReport(models.Model):
    PROMOTION_CHOICES = [
        ('Year 7 (Lower Secondary)', 'Year 7 (Lower Secondary)'),
        ('Year 8 (Lower Secondary)', 'Year 8 (Lower Secondary)'),
        ('Year 9 (Lower Secondary)', 'Year 9 (Lower Secondary)'),
        ('Year 10 (Upper Secondary)', 'Year 10 (Upper Secondary)'),
        ('Year 11 (Upper Secondary)', 'Year 11 (Upper Secondary)'),
        ('Year 12 (Sixth Form)', 'Year 12 (Sixth Form)'),
        ('Year 13 (Sixth Form)', 'Year 13 (Sixth Form)'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='academic_reports')
    student_scores = models.ManyToManyField(Score, related_name='academic_reports', blank=True)
    student_gpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_reports')
    
    # Comment fields
    academic_comment = models.TextField(blank=True, null=True)
    behavioral_comment = models.TextField(blank=True, null=True)
    promotion = models.CharField(max_length=100, choices=PROMOTION_CHOICES, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "End of Term Report"
        verbose_name_plural = "End of Term Reports"
        unique_together = ('student', 'term')

    def save(self, *args, **kwargs):
        # Calculate GPA using latest scores for subjects assigned to student
        # Always recalculate to ensure it's up-to-date
        scores = Score.objects.filter(
            student=self.student,
            term=self.term,
            subject__in=self.student.subjects.all()
        ).order_by('subject', '-updated_at').distinct('subject')

        if scores.exists():
            self.student_gpa = calculate_gpa(scores)
        else:
            self.student_gpa = Decimal('0.00')

        # Only allow promotion for Term 3
        if self.term.term_name != 'Term 3':
            self.promotion = None
        
        super().save(*args, **kwargs)

        # Always update student scores to ensure they're current
        # Use the same query as GPA calculation
        scores = Score.objects.filter(
            student=self.student,
            term=self.term,
            subject__in=self.student.subjects.all()
        ).order_by('subject', '-updated_at').distinct('subject')

        if scores.exists():
            self.student_scores.set(scores)

    def __str__(self):
        return f"Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.student_gpa}"

    def clean(self):
        # Validate that promotion is only set for Term 3
        if self.promotion and self.term and self.term.term_name != 'Term 3':
            raise ValidationError('Promotion can only be set for Term 3 reports.')
    
    @classmethod
    def get_or_create_report(cls, student, term, generated_by=None):
        """Get existing report or create a new one"""
        report, created = cls.objects.get_or_create(
            student=student,
            term=term,
            defaults={'generated_by': generated_by}
        )
        return report, created


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject, related_name='teachers')
    is_head_class_teacher = models.BooleanField(default=False)
    can_print_results = models.BooleanField(default=False, help_text="Allow user to print and download reports as PDF")

    class Meta:
        verbose_name="Teacher Profile"
        verbose_name_plural = "Teacher Profiles"

    def __str__(self):
        return f"Teacher Profile: {self.user.username}"




