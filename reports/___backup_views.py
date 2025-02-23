

class MidtermReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='midterm_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='midterm_reports')

    # Midterm GPA (calculated directly from the midterm_score field)
    midterm_gpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Linking related scores to the report (many-to-many relationship with Score)
    student_scores = models.ManyToManyField(Score, related_name='midterm_reports')

    # User who generated the report
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_midterm_reports')

    def calculate_gpa(self, scores):
        grade_points = []
        for score in scores:
            try:
                # Get the total score from the Score object (percentage out of 100)
                total_score = Decimal(score.midterm_score)

                # Calculate GPA based on proportional scale (0 - 100 scale)
                gpa = (total_score / Decimal(100)) * Decimal(4.0)
                
                # Add the GPA for this score to the list
                grade_points.append(gpa)
            except Exception as e:
                print(f"Error calculating GPA for score {score}: {e}")
                continue

        # Return the list of GPA points for valid scores
        return grade_points

    def save(self, *args, **kwargs):
        # Get the scores for the student in the current term
        scores = Score.objects.filter(student=self.student, term=self.term)

        # Calculate the total score and GPA
        total_scores = [score.midterm_score for score in scores]
        total_score_sum = sum(total_scores)
        average_score = total_score_sum / len(total_scores) if total_scores else 0
        gpa_points = self.calculate_gpa(scores)

        self.midterm_gpa = gpa_points

        # Link the scores to the report
        self.student_scores.set(scores)  # Many-to-many relationship with Score

        # Save the report
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Midterm Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.midterm_gpa}"


class ProgressiveTestOneReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progressive_test1_reports')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='progressive_test1_reports')

    # Progressive Test 1 GPA (calculated directly from the progressive_test_1_score field)
    progressive_test1_gpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Linking related scores to the report (many-to-many relationship with Score)
    student_scores = models.ManyToManyField(Score, related_name='progressive_test1_reports')

    # User who generated the report
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_progressive_test1_reports')

    def calculate_gpa(self, scores):
        grade_points = []
        for score in scores:
            try:
                # Get the total score from the Score object (percentage out of 100)
                total_score = Decimal(score.progressive_test_1_score)

                # Calculate GPA based on proportional scale (0 - 100 scale)
                gpa = (total_score / Decimal(100)) * Decimal(4.0)
                
                # Add the GPA for this score to the list
                grade_points.append(gpa)
            except Exception as e:
                print(f"Error calculating GPA for score {score}: {e}")
                continue

        # Return the list of GPA points for valid scores
        return grade_points

    def save(self, *args, **kwargs):
        # Get the scores for the student in the current term
        scores = Score.objects.filter(student=self.student, term=self.term)

        # Calculate the total score and GPA
        total_scores = [score.progressive_test_1_score for score in scores]
        total_score_sum = sum(total_scores)
        average_score = total_score_sum / len(total_scores) if total_scores else 0
        gpa_points = self.calculate_gpa(scores)

        self.progressive_test1_gpa = gpa_points

        # Link the scores to the report
        self.student_scores.set(scores)  # Many-to-many relationship with Score

        # Save the report
        super().save(*args, **kwargs)

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

    def calculate_gpa(self, scores):
        grade_points = []
        for score in scores:
            try:
                # Get the total score from the Score object (percentage out of 100)
                total_score = Decimal(score.progressive_test_2_score)

                # Calculate GPA based on proportional scale (0 - 100 scale)
                gpa = (total_score / Decimal(100)) * Decimal(4.0)
                
                # Add the GPA for this score to the list
                grade_points.append(gpa)
            except Exception as e:
                print(f"Error calculating GPA for score {score}: {e}")
                continue

        # Return the list of GPA points for valid scores
        return grade_points

    def save(self, *args, **kwargs):
        # Get the scores for the student in the current term
        scores = Score.objects.filter(student=self.student, term=self.term)

        # Calculate the total score and GPA
        total_scores = [score.progressive_test_2_score for score in scores]
        total_score_sum = sum(total_scores)
        average_score = total_score_sum / len(total_scores) if total_scores else 0
        gpa_points = self.calculate_gpa(scores)

        self.progressive_test2_gpa = gpa_points

        # Link the scores to the report
        self.student_scores.set(scores)  # Many-to-many relationship with Score

        # Save the report
        super().save(*args, **kwargs)

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

    def calculate_gpa(self, scores):
        grade_points = []
        for score in scores:
            try:
                # Get the total score from the Score object (percentage out of 100)
                total_score = Decimal(score.progressive_test_3_score)

                # Calculate GPA based on proportional scale (0 - 100 scale)
                gpa = (total_score / Decimal(100)) * Decimal(4.0)
                
                # Add the GPA for this score to the list
                grade_points.append(gpa)
            except Exception as e:
                print(f"Error calculating GPA for score {score}: {e}")
                continue

        # Return the list of GPA points for valid scores
        return grade_points

    def save(self, *args, **kwargs):
        # Get the scores for the student in the current term
        scores = Score.objects.filter(student=self.student, term=self.term)

        # Calculate the total score and GPA
        total_scores = [score.progressive_test_3_score for score in scores]
        total_score_sum = sum(total_scores)
        average_score = total_score_sum / len(total_scores) if total_scores else 0
        gpa_points = self.calculate_gpa(scores)

        # Set the GPA Points based on Progressive Test 3 Scores :
        self.progressive_test3_gpa = gpa_points

        # Link the scores to the report
        self.student_scores.set(scores)  # Many-to-many relationship with Score

        # Save the report
        super().save(*args, **kwargs)

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
                gpa = (total_score / Decimal(100)) * Decimal(4.0)
                
                # Add the GPA for this score to the list
                grade_points.append(gpa)
            except Exception as e:
                print(f"Error calculating GPA for score {score}: {e}")
                continue

        # Return the list of GPA points for valid scores
        return grade_points

    def __str__(self):
        return f"Report for {self.student.fullname} - {self.term.term_name} - GPA: {self.student_gpa}"
