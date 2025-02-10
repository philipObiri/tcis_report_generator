from django.db import models
from django.contrib.auth.models import User  
from decimal import Decimal

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
    class_work_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))
    progressive_test_1_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))
    progressive_test_2_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))
    progressive_test_3_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))
    midterm_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))

    # Exam score (main exam at the end of the term)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))

    continuous_assessment = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))
    grade = models.CharField(max_length=3, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Ensure that exam_score is never None, default to 0.0 if missing
        if self.exam_score is None:
            self.exam_score = Decimal('0.0')

        # Convert exam_score to Decimal in case it's a float or non-decimal value
        exam_score = Decimal(self.exam_score)

        # Calculate the sum of all the component scores
        total_continuous_assessment_score = (
            self.class_work_score +  # percentage score (out of 100%)
            self.progressive_test_1_score +  # percentage score (out of 100%)
            self.progressive_test_2_score +  # percentage score (out of 100%)
            self.progressive_test_3_score +  # percentage score (out of 100%)
            self.midterm_score  # percentage score (out of 100%)
        )

        # Normalize continuous_assessment to a 100% scale (total is out of 500, so divide by 500 and multiply by 100)
        self.continuous_assessment = (total_continuous_assessment_score / Decimal('500')) * Decimal('100')

        # Calculate Total Score: 30% of Continuous Assessment + 70% of Exam Score
        self.total_score = (self.continuous_assessment * Decimal('0.30')) + (exam_score * Decimal('0.70'))

        # Assign grade based on the total_score with the new grading scale
        if self.total_score >= Decimal('90'):
            self.grade = 'A+'
        elif self.total_score >= Decimal('80'):
            self.grade = 'A'
        elif self.total_score >= Decimal('75'):
            self.grade = 'B+'
        elif self.total_score >= Decimal('70'):
            self.grade = 'B'
        elif self.total_score >= Decimal('65'):
            self.grade = 'C+'
        elif self.total_score >= Decimal('60'):
            self.grade = 'C'
        elif self.total_score >= Decimal('50'):
            self.grade = 'D'
        elif self.total_score >= Decimal('45'):
            self.grade = 'E'
        elif self.total_score >= Decimal('35'):
            self.grade = 'F'
        else:
            self.grade = 'Ungraded'

        # Call the superclass save method to store the object in the database
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.fullname} - {self.subject.name} - {self.total_score}"



class AcademicReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='academic_reports')
    
    # Many to Many relation to the Score model to represent the student's individual scores
    student_scores = models.ManyToManyField(Score, related_name='academic_reports')
    student_gpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        scores = Score.objects.filter(student=self.student, term=self.term)
        grade_points = self.calculate_gpa(scores)
        
        if grade_points:
            self.student_gpa = sum(grade_points) / len(grade_points)
        
        super().save(*args, **kwargs)

    def calculate_gpa(self, scores):
        grade_points = []
        for score in scores:
            try:
                # Get the total score from the Score object (percentage out of 100)
                total_score = Decimal(score.total_score)

                # Calculate GPA based on proportional scale (0 - 100 scale)
                gpa = (total_score / Decimal(100)) * Decimal(5.0)
                
                # Add the GPA for this score to the list
                grade_points.append(gpa)
            except Exception as e:
                print(f"Error calculating GPA for score {score}: {e}")
                continue

        # Return the list of GPA points for valid scores
        return grade_points

    def __str__(self):
        return f"Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.student_gpa}"




# class AcademicReport(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_reports')
#     term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='academic_reports')
    
#     # Many to Many relation to the Score model to represent the student's individual scores
#     student_scores = models.ManyToManyField(Score, related_name='academic_reports')
#     student_gpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

#     def save(self, *args, **kwargs):
#         scores = Score.objects.filter(student=self.student, term=self.term)
#         grade_points = self.calculate_gpa(scores)
        
#         if grade_points:
#             self.student_gpa = sum(grade_points) / len(grade_points)
        
#         super().save(*args, **kwargs)

#     def calculate_gpa(self, scores):
#         grade_points = []
#         for score in scores:
#             grade = score.grade
#             # Update the GPA calculation logic based on new grading scale
#             if grade == 'A+':
#                 grade_points.append(4.5)
#             elif grade == 'A':
#                 grade_points.append(4.0)
#             elif grade == 'B+':
#                 grade_points.append(3.5)
#             elif grade == 'B':
#                 grade_points.append(3.0)
#             elif grade == 'C+':
#                 grade_points.append(2.5)
#             elif grade == 'C':
#                 grade_points.append(2.0)
#             elif grade == 'D':
#                 grade_points.append(1.0)
#             elif grade == 'E':
#                 grade_points.append(0.5)
#             elif grade == 'F':
#                 grade_points.append(0.0)
#             elif grade == 'Ungraded':
#                 grade_points.append(None)  # If ungraded, we don't calculate GPA for this score

#         # Filter out None values if there are any (students with 'Ungraded' scores won't affect GPA)
#         grade_points = [gp for gp in grade_points if gp is not None]

#         return grade_points

#     def __str__(self):
#         return f"Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.student_gpa}"




