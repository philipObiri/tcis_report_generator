from django.core.management.base import BaseCommand
from reports.models import Score, Student, Term


class Command(BaseCommand):
    help = 'Synchronize student comments across all subjects (comments are student-level, not subject-specific)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting comment synchronization...'))
        
        # Get all terms
        terms = Term.objects.all()
        total_students_updated = 0
        
        for term in terms:
            self.stdout.write(f'\nProcessing term: {term.term_name}')
            
            # Get all students with scores in this term
            students_with_scores = Student.objects.filter(
                scores__term=term
            ).distinct()
            
            for student in students_with_scores:
                # Get all scores for this student in this term
                student_scores = Score.objects.filter(student=student, term=term)
                
                # Find any score with comments
                academic_comment = None
                behavioral_comment = None
                
                for score in student_scores:
                    if score.academic_comment and not academic_comment:
                        academic_comment = score.academic_comment
                    if score.behavioral_comment and not behavioral_comment:
                        behavioral_comment = score.behavioral_comment
                    
                    # Break early if we found both
                    if academic_comment and behavioral_comment:
                        break
                
                # If we found any comments, apply them to ALL scores for this student in this term
                if academic_comment or behavioral_comment:
                    updated_count = student_scores.update(
                        academic_comment=academic_comment or '',
                        behavioral_comment=behavioral_comment or ''
                    )
                    
                    if updated_count > 0:
                        total_students_updated += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  [OK] Synced comments for {student.fullname} '
                                f'across {updated_count} subjects'
                            )
                        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n[SUCCESS] Comment synchronization complete! '
                f'Updated {total_students_updated} students'
            )
        )
