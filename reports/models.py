from django.db import models
from django.contrib.auth.models import User  
from decimal import Decimal

# Create your models here.
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



# ClassYear model
class ClassYear(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='level')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Class / Year'
        verbose_name_plural = 'Classes / Years'

    def __str__(self):
        return f"{self.level.name} - {self.name}"

# Term model to represent the three terms
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



# Subject model
class Subject(models.Model):
    name = models.CharField(max_length=100)
    class_year = models.ManyToManyField(ClassYear,related_name='subjects')
    def __str__(self):
        return self.name




class Student(models.Model):
    fullname = models.CharField(max_length=255)
    class_year = models.ForeignKey(ClassYear, on_delete=models.CASCADE, related_name='students')
    subjects = models.ManyToManyField(Subject, related_name='students', blank=True)

    def __str__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        # First save the student to generate the primary key (if it's a new instance)
        created = self.pk is None
        super().save(*args, **kwargs)

        # After the student is saved, assign subjects based on class_year
        if created or self._state.fields_cache.get('class_year') != self.class_year:
            # Assign the subjects based on the class_year
            self.subjects.set(self.class_year.subjects.all())

        # Save the many-to-many relationship
        self.save_m2m()  # This ensures the many-to-many relationship is saved after it's updated

    def save_m2m(self):
        # Django requires a separate call to save many-to-many fields
        if self.pk:  # Ensure that the student has been saved and has an ID before saving m2m
            self.subjects.clear()  # Clear any existing subjects before setting new ones
            self.subjects.add(*self.class_year.subjects.all())  # Add the subjects




# Score model to store each student's assessment and exam score
class Score(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='scores')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='scores')  # Link score to term

    continuous_assessment = models.DecimalField(max_digits=5, decimal_places=2)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_score = models.DecimalField(max_digits=5, decimal_places=2)

    grade = models.CharField(max_length=3, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Use Decimal instead of float for calculations
        self.total_score = (self.continuous_assessment * Decimal('0.3')) + (self.exam_score * Decimal('0.7'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.fullname} - {self.subject.name} - {self.total_score}"





class AcademicReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='academic_reports')
    
    # Many to Many rel to the Score model to represent the student's individual scores
    student_scores = models.ManyToManyField(Score, related_name='academic_reports')
    # The student's GPA for the given term
    student_gpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Fetch all scores for the student in the given term
        scores = Score.objects.filter(student=self.student, term=self.term)
        
        # Calculate GPA using the grade point scale
        grade_points = self.calculate_gpa(scores)
        
        # Calculate GPA by averaging the grade points
        if grade_points:
            self.student_gpa = sum(grade_points) / len(grade_points)
        
        super().save(*args, **kwargs)

    def calculate_gpa(self, scores):
        grade_points = []
        for score in scores:
            grade = score.grade
            
            # Mapping grades to grade points
            if grade == 'A*':
                grade_points.append(4.0)
            elif grade == 'A':
                grade_points.append(3.75)
            elif grade == 'B':
                grade_points.append(3.0)
            elif grade == 'C':
                grade_points.append(2.0)
            elif grade == 'D':
                grade_points.append(1.0)
            elif grade == 'F':
                grade_points.append(0.0)
        
        return grade_points

    def __str__(self):
        return f"Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.student_gpa}"
