from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Student(models.Model):
    fullname = models.CharField(max_length=200)
    student_id = models.CharField(max_length=50, unique=True)
    # Add other student fields as needed
    
    def __str__(self):
        return self.fullname

class ClassYear(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., "Year 7 (Lower Secondary)"
    level = models.CharField(max_length=50)  # e.g., "Lower Secondary"
    
    def __str__(self):
        return self.name

class Term(models.Model):
    TERM_CHOICES = [
        ('Term 1', 'Term 1'),
        ('Term 2', 'Term 2'),
        ('Term 3', 'Term 3'),
    ]
    
    term_name = models.CharField(max_length=20, choices=TERM_CHOICES)
    class_year = models.ForeignKey(ClassYear, on_delete=models.CASCADE, related_name='terms')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ('term_name', 'class_year')
    
    def __str__(self):
        return f"{self.term_name} - {self.class_year.name}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name

class Score(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='scores')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='scores')
    continuous_assessment = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'term')
    
    def __str__(self):
        return f"{self.student.fullname} - {self.subject.name} - {self.term.term_name}"
    
    @property
    def total_score(self):
        ca = self.continuous_assessment or 0
        exam = self.exam_score or 0
        return ca + exam

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    is_head_class_teacher = models.BooleanField(default=False)
    # Add other teacher fields as needed
    
    def __str__(self):
        return f"{self.user.username} - Head Class Teacher: {self.is_head_class_teacher}"

def calculate_gpa(scores):
    """Calculate GPA from scores"""
    if not scores.exists():
        return 0.00
    
    total_points = 0
    total_subjects = 0
    
    for score in scores:
        total_score = score.total_score
        
        # Convert total score to grade points
        if total_score >= 95:
            grade_points = 4.00
        elif total_score >= 80:
            grade_points = 3.67
        elif total_score >= 75:
            grade_points = 3.33
        elif total_score >= 70:
            grade_points = 3.00
        elif total_score >= 65:
            grade_points = 2.67
        elif total_score >= 60:
            grade_points = 2.33
        elif total_score >= 50:
            grade_points = 2.00
        elif total_score >= 45:
            grade_points = 1.67
        elif total_score >= 35:
            grade_points = 1.00
        else:
            grade_points = 0.00
        
        total_points += grade_points
        total_subjects += 1
    
    return round(total_points / total_subjects, 2) if total_subjects > 0 else 0.00

def get_grade(total_score):
    """Get letter grade from total score"""
    if total_score >= 95:
        return 'A*'
    elif total_score >= 80:
        return 'A'
    elif total_score >= 75:
        return 'B+'
    elif total_score >= 70:
        return 'B'
    elif total_score >= 65:
        return 'C+'
    elif total_score >= 60:
        return 'C'
    elif total_score >= 50:
        return 'D'
    elif total_score >= 45:
        return 'E'
    elif total_score >= 35:
        return 'F'
    else:
        return 'Ungraded'

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
        # Calculate GPA if not already set
        if not self.student_gpa:
            scores = Score.objects.filter(student=self.student, term=self.term)
            if scores.exists():
                self.student_gpa = calculate_gpa(scores)
        
        # Only allow promotion for Term 3
        if self.term.term_name != 'Term 3':
            self.promotion = None
        
        super().save(*args, **kwargs)
        
        # Set student scores if not already set
        if not self.student_scores.exists():
            scores = Score.objects.filter(student=self.student, term=self.term)
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