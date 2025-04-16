from django.db import models
from django.contrib.auth.models import User  
from decimal import Decimal,ROUND_HALF_UP
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
    name = models.CharField(max_length=100)
    class_year = models.ManyToManyField(ClassYear, related_name='subjects')

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


class Score(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='scores')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='scores')

    # New fields for individual scores
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
    grade = models.CharField(max_length=255, blank=True)  # Changed max_length to 100

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate the sum of all the component scores
        total_continuous_assessment_score = (
            self.class_work_score +
            self.progressive_test_1_score +
            self.progressive_test_2_score +
            self.progressive_test_3_score +
            self.midterm_score
        )

        # Normalize continuous_assessment to a 100% scale (total is out of 500)
        normalized_continuous_assessment = (total_continuous_assessment_score / Decimal('500')) * Decimal('100')

        # Calculate Continuous Assessment as 30% of normalized value
        self.continuous_assessment = normalized_continuous_assessment * Decimal('0.30')

        # Calculate Total Score: 30% of CA + 70% of exam
        raw_total_score = self.continuous_assessment + (self.exam_score * Decimal('0.70'))

        # Round total_score to the nearest whole number
        self.total_score = raw_total_score.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        # Assign grade based on rounded total_score
        if Decimal('95') <= self.total_score <= Decimal('100'):
            self.grade = 'A*'
        elif Decimal('80') <= self.total_score <= Decimal('94'):
            self.grade = 'A'
        elif Decimal('75') <= self.total_score <= Decimal('79'):
            self.grade = 'B+'
        elif Decimal('70') <= self.total_score <= Decimal('74'):
            self.grade = 'B'
        elif Decimal('65') <= self.total_score <= Decimal('69'):
            self.grade = 'C+'
        elif Decimal('60') <= self.total_score <= Decimal('64'):
            self.grade = 'C'
        elif Decimal('50') <= self.total_score <= Decimal('59'):
            self.grade = 'D'
        elif Decimal('45') <= self.total_score <= Decimal('49'):
            self.grade = 'E'
        elif Decimal('35') <= self.total_score <= Decimal('44'):
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


class ProgressiveTestThreeReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progressive_test3_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='progressive_test3_reports')

    # Progressive Test 3 GPA (calculated directly from the progressive_test_3_score field)
    progressive_test3_gpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Linking related scores to the report (many-to-many relationship with Score)
    student_scores = models.ManyToManyField(Score, related_name='progressive_test3_reports')

    # User who generated the report
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_progressive_test3_reports')

    class Meta:
        verbose_name = "Progressive Three Report"
        verbose_name_plural = "Progressive Three Reports"

    def save(self, *args, **kwargs):
        # Ensure the user who generated the report is set automatically
        if not self.generated_by and 'user' in kwargs:
            self.generated_by = kwargs.pop('user', None)

        # Get the scores for the student in the current term
        scores = Score.objects.filter(student=self.student, term=self.term)

        # Fetch the progressive test score three for each score:
        total_scores = [score.progressive_test_3_score for score in scores]

        # Calculate GPA using the external calculate_gpa function (assuming you have a `calculate_gpa` function)
        gpa = calculate_gpa(total_scores)

        # Set the progressive_test3_gpa based on the calculated GPA
        self.progressive_test3_gpa = gpa

        # Save the report first to generate an ID (needed for Many-to-Many relationship)
        super().save(*args, **kwargs)

        # Now link the scores to the report (many-to-many relationship)
        self.student_scores.set(scores)  # Many-to-many relationship with Scores: progressive test scores

        # Save the many-to-many relationship. Django will handle this automatically when you call 'set()'.
        # Just calling self.save() again will ensure everything is persisted.

    def __str__(self):
        return f"Progressive Test 3 Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.progressive_test3_gpa}"



class AcademicReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='academic_reports')

    # Many to Many relation to the Score model to represent the student's individual scores
    student_scores = models.ManyToManyField(Score, related_name='academic_reports')
    student_gpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # ForeignKey to the User model (user who generated the report)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_reports')

    class Meta:
        verbose_name = "End of Term Report"
        verbose_name_plural = "End of Term Reports"

    def save(self, *args, **kwargs):
        # Check if this report already exists for the given student and term
        existing_report = AcademicReport.objects.filter(student=self.student, term=self.term).first()

        if existing_report:
            # If the report exists, just update the fields and save it
            self.pk = existing_report.pk  # Set the primary key to the existing report's pk
            self.student_gpa = existing_report.student_gpa  # If needed, update the GPA
        else:
            # If the report doesn't exist, proceed with creating a new one
            scores = Score.objects.filter(student=self.student, term=self.term)

            # Calculate GPA using the external calculate_gpa function
            gpa = calculate_gpa(scores)
            self.student_gpa = gpa

        # Now save the report (either update or create)
        super().save(*args, **kwargs)

        # Set the ManyToManyField after saving the object to ensure the ID is set
        scores = Score.objects.filter(student=self.student, term=self.term)
        self.student_scores.set(scores)

    def __str__(self):
        return f"Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.student_gpa}"



class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    subjects = models.ManyToManyField(Subject, related_name='teachers')
    class Meta:
        verbose_name="Teacher Profile"
        verbose_name_plural = "Teacher Profiles"
    
    def __str__(self):
        return f"Teacher Profile: {self.user.username}"


