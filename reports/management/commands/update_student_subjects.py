from django.core.management.base import BaseCommand
from reports.models import Student
from django.db import transaction

class Command(BaseCommand):
    help = 'Clears and reassigns subjects for all students based on their class year.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to update subjects for all students...")

        try:
            self.update_student_subjects()
            self.stdout.write(self.style.SUCCESS("Subjects reassigned successfully."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))

    def update_student_subjects(self):
        # Start a transaction to ensure the operations are atomic
        with transaction.atomic():
            # Fetch all students
            students = Student.objects.all()

            # Loop through each student
            for student in students:
                # Clear the current subjects assigned to the student
                student.subjects.clear()

                # Assign the subjects related to the student's class_year
                subjects_for_class_year = student.class_year.subjects.all()
                student.subjects.set(subjects_for_class_year)

                # Save the student instance after reassigning the subjects
                student.save()

            self.stdout.write("Subjects reassigned successfully.")
