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

        # Ensure the total_score is a valid percentage value between 0 and 100
        self.total_score = min(max(self.total_score, Decimal('0.0')), Decimal('100.0'))

        # Assign grade based on the total_score with the new grading scale using range checks
        if self.total_score >= Decimal('95') and self.total_score <= Decimal('100'):
            self.grade = 'A*'  # GPA: 4.00
        elif self.total_score >= Decimal('80') and self.total_score < Decimal('95'):
            self.grade = 'A'   # GPA: 3.67
        elif self.total_score >= Decimal('75') and self.total_score < Decimal('80'):
            self.grade = 'B+'  # GPA: 3.33
        elif self.total_score >= Decimal('70') and self.total_score < Decimal('75'):
            self.grade = 'B'   # GPA: 3.00
        elif self.total_score >= Decimal('65') and self.total_score < Decimal('70'):
            self.grade = 'C+'  # GPA: 2.67
        elif self.total_score >= Decimal('60') and self.total_score < Decimal('65'):
            self.grade = 'C'   # GPA: 2.33
        elif self.total_score >= Decimal('50') and self.total_score < Decimal('60'):
            self.grade = 'D'   # GPA: 2.00
        elif self.total_score >= Decimal('45') and self.total_score < Decimal('50'):
            self.grade = 'E'   # GPA: 1.67
        elif self.total_score >= Decimal('35') and self.total_score < Decimal('45'):
            self.grade = 'F'   # GPA: 1.00
        else:
            self.grade = 'Ungraded'  # GPA: 0.00

        # Call the superclass save method to store the object in the database
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.fullname} - {self.subject.name} - {self.total_score}"
