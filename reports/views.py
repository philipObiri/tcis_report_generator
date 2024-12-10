from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Level, ClassYear, Term, Subject, Student, Score, AcademicReport
from .forms import ScoreForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Score
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Student, Term, Score, AcademicReport
from django.shortcuts import render
from django.http import JsonResponse
from .models import AcademicReport, Term, Student, Score
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Student, Term, Score, AcademicReport
import json

def custom_login(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')  # Could be either username or email
        password = request.POST.get('password')

        # Try to authenticate with username or email
        user = None
        if '@' in username_or_email:  # Check if input is an email
            user = authenticate(request, username=username_or_email, password=password)
        else:  # Otherwise treat it as a username
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)
            return redirect('process_scores')  # Redirect to the homepage or a desired page after login
        else:
            # If authentication fails, show an error message
            messages.error(request, 'Invalid username/email or password')

    return render(request, 'login.html')


# Logout View
def custom_logout(request):
    logout(request)
    return redirect('login')  # Redirect to home or the desired page after logout



# Display saved scores for the user
def process_scores_view(request):
    formset = None
    students = []
    scores = []

    students = Student.objects.all()  # Adjust as per your filter
    scores = Score.objects.filter(created_by=request.user)  # Fetch all scores, can be filtered if needed

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Process the submitted scores and save them to the database
        level_id = request.POST.get('level')
        class_year_id = request.POST.get('class_year')
        term_id = request.POST.get('term')
        subject_id = request.POST.get('subject')

        level = Level.objects.get(id=level_id) if level_id else None
        class_year = ClassYear.objects.get(id=class_year_id) if class_year_id else None
        term = Term.objects.get(id=term_id) if term_id else None
        subject = Subject.objects.get(id=subject_id) if subject_id else None

        if class_year:
            students = Student.objects.filter(class_year=class_year)

        for student in students:
            continuous_assessment = request.POST.get(f'continuous_assessment_{student.id}')
            exam_score = request.POST.get(f'exam_score_{student.id}')
            
            if continuous_assessment and exam_score:
                continuous_assessment = float(continuous_assessment)
                exam_score = float(exam_score)

                total_score = (continuous_assessment * 0.3) + (exam_score * 0.7)

                if total_score >= 90:
                    grade = 'A*'
                elif total_score >= 80:
                    grade = 'A'
                elif total_score >= 70:
                    grade = 'B'
                elif total_score >= 60:
                    grade = 'C'
                elif total_score >= 50:
                    grade = 'D'
                else:
                    grade = 'F'

                score_instance, created = Score.objects.update_or_create(
                    student=student,
                    term=term,
                    subject=subject,
                    continuous_assessment=continuous_assessment,
                    exam_score=exam_score,
                    total_score=total_score,
                    grade=grade,
                    created_by=request.user
                )

        return JsonResponse({'status': 'success', 'message': 'Scores saved successfully!'})

    return render(request, 'index.html', {
        'formset': formset,
        'students': students,
        'scores': scores,
    })



@login_required
def get_saved_scores(request):
    scores = Score.objects.filter(created_by=request.user).select_related('student')
    
    # Serialize scores into a dictionary format for rendering
    scores_data = [{
        'student_name': score.student.fullname,
        'score_id': score.id,
        'grade': score.grade,
        'student_id': score.student.id
    } for score in scores]

    return JsonResponse({'scores': scores_data})



def view_academic_report(request, student_id, term_id):
    try:
        student = Student.objects.get(id=student_id)
        scores = Score.objects.filter(student=student, term=term_id)
        term = get_object_or_404(Term, id=term_id)
        
        # Ensure that class_year is serialized to a string or relevant field
        class_year = student.class_year.name if hasattr(student.class_year, 'name') else str(student.class_year)

        # Calculate GPA based on scores (e.g., using weighted average of grades)
        gpa = calculate_gpa(scores)

        # Prepare data to be returned in the JSON response
        report = {
            'student_name': student.fullname,
            'class_year': class_year,  # Ensure it's a serializable value (e.g., string)
            'term': term.term_name,
            'gpa': gpa,
            'scores': [
                {
                    'subject': score.subject.name,
                    'ca': score.continuous_assessment,
                    'exam': score.exam_score,
                    'total': score.total_score,  # Assuming you have a method to calculate total score
                    'grade': score.grade
                }
                for score in scores
            ]
        }

        # Return a JsonResponse with the report data
        return JsonResponse(report)

    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def get_levels(request):
    levels = Level.objects.all()

    # Serialize the levels into a list of dictionaries
    levels_data = [{'id': level.id, 'name': level.name} for level in levels]

    return JsonResponse({"levels": levels_data})


# Fetch classes based on selected level
def get_classes_by_level(request, level_id):
    try:
        level = Level.objects.get(id=level_id)
        class_years = ClassYear.objects.filter(level=level)
        
        # Serialize the class_years into a list of dictionaries
        class_years_data = [{'id': class_year.id, 'name': class_year.name} for class_year in class_years]

        return JsonResponse({'class_years': class_years_data})
    except Level.DoesNotExist:
        return JsonResponse({'error': 'Level not found'}, status=404)


# Fetch terms based on selected class year
def get_terms_by_class_year(request, class_year_id):
    try:
        class_year = ClassYear.objects.get(id=class_year_id)
        terms = Term.objects.filter(class_year=class_year)
        
        # Serialize the terms into a list of dictionaries
        terms_data = [{'id': term.id, 'name': term.term_name} for term in terms]

        return JsonResponse({'terms': terms_data})
    except ClassYear.DoesNotExist:
        return JsonResponse({'error': 'Class Year not found'}, status=404)


# Fetch subjects based on selected class year
def get_subjects_by_class_year(request, class_year_id):
    try:
        class_year = ClassYear.objects.get(id=class_year_id)
        subjects = Subject.objects.filter(class_year=class_year)
        
        # Serialize the subjects into a list of dictionaries
        subjects_data = [{'id': subject.id, 'name': subject.name} for subject in subjects]

        return JsonResponse({'subjects': subjects_data})
    except ClassYear.DoesNotExist:
        return JsonResponse({'error': 'Class Year not found'}, status=404)


# Fetch students based on selected filters
def get_students_by_filters(request, level_id, class_year_id, term_id, subject_id):
    try:
        # Get the selected objects based on the filters
        level = Level.objects.get(id=level_id)
        class_year = ClassYear.objects.get(id=class_year_id)
        term = Term.objects.get(id=term_id)
        subject = Subject.objects.get(id=subject_id)

        # Fetch students based on the selected class year
        students = Student.objects.filter(class_year=class_year)

        # Fetch the corresponding scores for each student for the selected term and subject
        scores = Score.objects.filter(student__in=students, term=term, subject=subject)

        # Prepare the student data for serialization
        student_data = []
        for student in students:
            # Get the scores for each student
            student_scores = scores.filter(student=student)

            # Serialize the student and their scores into a dictionary
            student_info = {
                'student_id': student.id,
                'student_name': student.fullname,  # assuming 'fullname' is a field in your Student model
                'scores': []
            }

            # Collect the student's scores
            for score in student_scores:
                student_info['scores'].append({
                    'score_id': score.id,
                    'score_grade': score.grade,  # assuming 'score_value' is a field in your Score model
                    'continuous_assessment': score.continuous_assessment,  # Adjust as needed
                    'exam_score': score.exam_score  # Adjust as needed
                })

            # Add the student's information to the list
            student_data.append(student_info)

        # Return the serialized student data along with the subject name
        return JsonResponse({
            'student_data': student_data,
            'subject_name': subject.name  # Include subject name here
        })

    except (Level.DoesNotExist, ClassYear.DoesNotExist, Term.DoesNotExist, Subject.DoesNotExist):
        return JsonResponse({'error': 'Invalid filter parameters'}, status=404)




def delete_score(request, score_id):
    if request.method == 'DELETE':
        try:
            print(f"Deleting score with ID: {score_id}")
            score = Score.objects.get(pk=score_id)
            score.delete()
            return JsonResponse({"status": "success", "message": "Score deleted successfully"})
        except Score.DoesNotExist:
            print(f"Score with ID {score_id} not found.")
            return JsonResponse({"status": "error", "message": "Score not found"}, status=404)
    print(f"Invalid request method: {request.method}")
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)



from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import AcademicReport, Student, Term, ClassYear, Score
import json

def generate_report(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        student_name = data.get('student_name')
        class_year = data.get('class_year')
        term_name = data.get('term')

        try:
            # Fetch the student, class_year, and term objects
            student = Student.objects.get(fullname=student_name)
            class_year_obj = ClassYear.objects.get(name=class_year)
            term = Term.objects.get(term_name=term_name, class_year=class_year_obj)

            # Check if there are scores for the student in the selected term
            scores = Score.objects.filter(student=student, term=term)

            if not scores.exists():
                return JsonResponse({
                    'success': False,
                    'error': f'No scores found for {student_name} in {term_name}.'
                })

            # Create or update the AcademicReport instance for this student and term
            academic_report, created = AcademicReport.objects.get_or_create(
                student=student,
                term=term
            )

            # If it's a new report, assign the scores to the report and calculate GPA
            if created:
                academic_report.student_scores.set(scores)  # Assign the scores to the report

            # Save the academic report which will trigger GPA calculation
            academic_report.save()  # The GPA will be automatically calculated by the model's save method

            # Render the HTML for the report using the 'generated_report.html' template
            report_html = render_to_string('generated_report.html', {
                'student_name': student_name,
                'class_year': class_year,
                'term_name': term_name,
                'gpa': academic_report.student_gpa,
                'report_data': academic_report.student_scores.all(),  # Assuming student_scores are needed
            })

            # Return the HTML content in the JSON response
            return JsonResponse({
                'success': True,
                'report_html': report_html  # Pass the generated HTML content
            })

        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Student not found.'})
        except Term.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Term not found.'})
        except ClassYear.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Class Year not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})





def generate_academic_report(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            term_id = data.get('term_id')

            # Get the student and term objects
            student = get_object_or_404(Student, id=student_id)
            term = get_object_or_404(Term, id=term_id)

            # Fetch the student's scores for the given term
            scores = Score.objects.filter(student=student, term=term)

            # Create the academic report instance
            academic_report = AcademicReport(
                student=student,
                term=term,
                student_score=scores.first(),  # Assuming there's at least one score
            )
            academic_report.save()  # Save the report to the database

            # Calculate GPA for the student
            gpa = academic_report.student_gpa  # The GPA is calculated when saving the report

            # Prepare the data for the response
            report_data = {
                'student_name': student.fullname,
                'class_year': student.class_year.name,  # Ensure it's a string or serializable field
                'term': term.term_name,
                'gpa': gpa,
                'scores': [
                    {
                        'subject': score.subject.name,
                        'ca': score.continuous_assessment,
                        'exam': score.exam_score,
                        'total': score.total_score,
                        'grade': score.grade,
                    }
                    for score in scores
                ]
            }

            return JsonResponse(report_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



def calculate_gpa(scores):
    """
    Calculate the GPA from a list of scores using simple logic.
    Adjust this logic if necessary.
    """
    total_points = 0
    total_subjects = len(scores)
    
    for score in scores:
        if score.grade == 'A':
            total_points += 4.0
        elif score.grade == 'B':
            total_points += 3.0
        elif score.grade == 'C':
            total_points += 2.0
        elif score.grade == 'D':
            total_points += 1.0
        else:
            total_points += 0.0

    return total_points / total_subjects if total_subjects > 0 else 0.0


