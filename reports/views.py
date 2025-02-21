from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib import messages
from .models import Level, ClassYear, Term, Subject, Student, Score, AcademicReport
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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import AcademicReport, Student, Term, ClassYear, Score
import json
from decimal import Decimal 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt  # Import csrf_exempt


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
            return redirect('select_option')  # Redirect to the homepage or a desired page after login
        else:
            # If authentication fails, show an error message
            messages.error(request, 'Invalid username/email or password')

    return render(request, 'login.html')


#==================== Logout View ====================
def custom_logout(request):
    logout(request)
    return redirect('login')  # Redirect to home or the desired page after logout


#====================Select Option View ====================
@login_required(login_url='login')
def select_option(request):
    template = "index.html"
    context = {}
    return render (request, template, context)



#==================== Select Progressive Option View ====================
@login_required(login_url='login')
def select_progressive_option(request):
    template = "progressive_tests/progressive_option.html"
    context = {}
    return render (request, template, context)



#============ Process Class Scores ================
@login_required(login_url='login')
def class_scores(request):
    students = []
    scores = []
    term = None
    subject = None

    students = Student.objects.all()

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Retrieve POST parameters for filters
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

        # Process the submitted classwork scores
        for student in students:
            existing_score = Score.objects.filter(
                student=student,
                term=term,
                subject=subject,
                created_by=request.user
            ).first()

            class_work_score = 0

            if existing_score:
                class_work_score = existing_score.class_work_score

            posted_class_score = request.POST.get(f'class_score_{student.id}')
            if posted_class_score:
                try:
                    class_work_score = Decimal(posted_class_score)

                    score_instance, created = Score.objects.update_or_create(
                        student=student,
                        term=term,
                        subject=subject,
                        created_by=request.user,
                        defaults={'class_work_score': class_work_score}
                    )

                    # Recalculate after saving the class score
                    score_instance.save()

                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Invalid score value for {student.fullname}.'
                    })

        return JsonResponse({
            'status': 'success',
            'message': 'Classwork scores saved successfully!'
        })

    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')
    
    if term_id and subject_id:
        term = Term.objects.get(id=term_id)
        subject = Subject.objects.get(id=subject_id)
        scores = Score.objects.filter(term=term, subject=subject, created_by=request.user)

    return render(request, 'class_scores.html', {
        'students': students,
        'scores': scores,
    })



#=========== Process First Progressive Test Scores =====================
@login_required(login_url='login')
def progressive_test_scores_one(request):
    students = []
    scores = []
    term = None
    subject = None

    if request.method == 'POST':
        level_id = request.POST.get('level')
        class_year_id = request.POST.get('class_year')
        term_id = request.POST.get('term')
        subject_id = request.POST.get('subject')

        if class_year_id:
            class_year = ClassYear.objects.get(id=class_year_id)
            students = Student.objects.filter(class_year=class_year)
        else:
            students = Student.objects.all()

        term = Term.objects.get(id=term_id) if term_id else None
        subject = Subject.objects.get(id=subject_id) if subject_id else None

        for student in students:
            progressive_test_1_score = request.POST.get(f'progressive_test_1_score_{student.id}')
            if progressive_test_1_score:
                try:
                    progressive_test_1_score = Decimal(progressive_test_1_score)
                except ValueError:
                    progressive_test_1_score = None

                Score.objects.update_or_create(
                    student=student,
                    term=term,
                    subject=subject,
                    created_by=request.user,
                    defaults={'progressive_test_1_score': progressive_test_1_score}
                )

                # Ensure recalculation after saving the score
                score_instance = Score.objects.get(student=student, term=term, subject=subject, created_by=request.user)
                score_instance.save()

        messages.success(request, 'Progressive test data saved successfully.')

        return redirect('progressive_score_one')

    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')

    if term_id and subject_id:
        term = Term.objects.get(id=term_id)
        subject = Subject.objects.get(id=subject_id)
        scores = Score.objects.filter(term=term, subject=subject, created_by=request.user)

    context = {
        'students': students,
        'scores': scores,
    }

    return render(request, 'progressive_tests/progressive_test_1.html', context)





#=========== Process Second Progressive Test Scores =====================
@login_required(login_url='login')
def progressive_test_scores_two(request):
    students = []
    scores = []
    term = None
    subject = None

    if request.method == 'POST':
        level_id = request.POST.get('level')
        class_year_id = request.POST.get('class_year')
        term_id = request.POST.get('term')
        subject_id = request.POST.get('subject')

        if class_year_id:
            class_year = ClassYear.objects.get(id=class_year_id)
            students = Student.objects.filter(class_year=class_year)
        else:
            students = Student.objects.all()

        term = Term.objects.get(id=term_id) if term_id else None
        subject = Subject.objects.get(id=subject_id) if subject_id else None

        for student in students:
            progressive_test_2_score = request.POST.get(f'progressive_test_2_score_{student.id}')
            if progressive_test_2_score:
                try:
                    progressive_test_2_score = Decimal(progressive_test_2_score)
                except ValueError:
                    progressive_test_2_score = None

                Score.objects.update_or_create(
                    student=student,
                    term=term,
                    subject=subject,
                    created_by=request.user,
                    defaults={'progressive_test_2_score': progressive_test_2_score}
                )

                # Ensure recalculation after saving the score
                score_instance = Score.objects.get(student=student, term=term, subject=subject, created_by=request.user)
                score_instance.save()

        messages.success(request, 'Progressive Test 2 data saved successfully.')

        return redirect('progressive_score_two')

    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')

    if term_id and subject_id:
        term = Term.objects.get(id=term_id)
        subject = Subject.objects.get(id=subject_id)
        scores = Score.objects.filter(term=term, subject=subject, created_by=request.user)

    context = {
        'students': students,
        'scores': scores,
    }

    return render(request, 'progressive_tests/progressive_test_2.html', context)




#=========== Process Third Progressive Test Scores =====================
@login_required(login_url='login')
def progressive_test_scores_three(request):
    students = []
    scores = []
    term = None
    subject = None

    if request.method == 'POST':
        level_id = request.POST.get('level')
        class_year_id = request.POST.get('class_year')
        term_id = request.POST.get('term')
        subject_id = request.POST.get('subject')

        if class_year_id:
            class_year = ClassYear.objects.get(id=class_year_id)
            students = Student.objects.filter(class_year=class_year)
        else:
            students = Student.objects.all()

        term = Term.objects.get(id=term_id) if term_id else None
        subject = Subject.objects.get(id=subject_id) if subject_id else None

        for student in students:
            progressive_test_3_score = request.POST.get(f'progressive_test_3_score_{student.id}')
            if progressive_test_3_score:
                try:
                    progressive_test_3_score = Decimal(progressive_test_3_score)
                except ValueError:
                    progressive_test_3_score = None

                Score.objects.update_or_create(
                    student=student,
                    term=term,
                    subject=subject,
                    created_by=request.user,
                    defaults={'progressive_test_3_score': progressive_test_3_score}
                )

                # Ensure recalculation after saving the score
                score_instance = Score.objects.get(student=student, term=term, subject=subject, created_by=request.user)
                score_instance.save()

        messages.success(request, 'Progressive Test 3 data saved successfully.')

        return redirect('progressive_score_three')

    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')

    if term_id and subject_id:
        term = Term.objects.get(id=term_id)
        subject = Subject.objects.get(id=subject_id)
        scores = Score.objects.filter(term=term, subject=subject, created_by=request.user)

    context = {
        'students': students,
        'scores': scores,
    }

    return render(request, 'progressive_tests/progressive_test_3.html', context)



#========== Process MidTerm Scores ====================
@login_required(login_url='login')
def midterm_scores(request):
    students = []
    scores = []
    term = None
    subject = None

    students = Student.objects.all()

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Retrieve POST parameters for filters
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
            existing_score = Score.objects.filter(
                student=student,
                term=term,
                subject=subject,
                created_by=request.user
            ).first()

            midterm_score = 0

            if existing_score:
                midterm_score = existing_score.midterm_score

            posted_midterm_score = request.POST.get(f'midterm_score_{student.id}')
            if posted_midterm_score:
                try:
                    midterm_score = Decimal(posted_midterm_score)

                    score_instance, created = Score.objects.update_or_create(
                        student=student,
                        term=term,
                        subject=subject,
                        created_by=request.user,
                        defaults={'midterm_score': midterm_score}
                    )

                    # Recalculate after saving the midterm score
                    score_instance.save()

                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Invalid midterm score value for {student.fullname}.'
                    })

        return JsonResponse({
            'status': 'success',
            'message': 'Midterm scores saved successfully!'
        })

    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')

    if term_id and subject_id:
        term = Term.objects.get(id=term_id)
        subject = Subject.objects.get(id=subject_id)
        scores = Score.objects.filter(term=term, subject=subject, created_by=request.user)

    context = {
        'students': students,
        'scores': scores,
    }

    return render(request, 'midterm.html', context)




##=============== Process and Display Saved End of Term Scores for the user ===============
@login_required(login_url='login')
def process_scores_view(request):
    formset = None
    students = []
    scores = []

    # Fetch all students and their scores (including continuous_assessment) for the logged-in user
    students = Student.objects.all()  # Adjust as per your filter
    scores = Score.objects.filter(created_by=request.user)  # Fetch scores entered by the logged-in user

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
            # Fetch existing score for the student, term, and subject
            existing_score = Score.objects.filter(
                student=student,
                term=term,
                subject=subject,
                created_by=request.user
            ).first()

            # Fetch the exam score from POST request (it may not exist if the user didn't input it)
            exam_score = request.POST.get(f'exam_score_{student.id}', 0.0)

            try:
                # Convert exam_score to Decimal, if it's not 0.0
                exam_score = Decimal(str(exam_score)) if exam_score else Decimal('0.0')
            except:
                exam_score = Decimal('0.0')  # If the value can't be converted, set to 0.0

            # If a score exists for the student, use that to fetch or update the score
            if existing_score:
                # Update existing score (don't manually recalculate)
                existing_score.exam_score = exam_score
                existing_score.save()  # This will trigger the `save()` method to recalculate total_score and grade
            else:
                # Create a new score object if no existing score
                new_score = Score(
                    student=student,
                    term=term,
                    subject=subject,
                    created_by=request.user,
                    exam_score=exam_score,
                )
                new_score.save()  # This will trigger the `save()` method to calculate total_score and grade

        return JsonResponse({'status': 'success', 'message': 'End of Term Scores saved successfully!'})

    return render(request, 'dashboard.html', {
        'formset': formset,
        'students': students,
        'scores': scores,
    })





@login_required(login_url='login')
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




# # Fetch students based on selected filters
def get_students_by_filters(request, level_id, class_year_id, term_id, subject_id):
    try:
        # Get the selected objects based on the filters
        level = Level.objects.get(id=level_id)
        class_year = ClassYear.objects.get(id=class_year_id)
        term = Term.objects.get(id=term_id)
        subject = Subject.objects.get(id=subject_id)

        # Fetch students based on the selected class year and subject
        students = Student.objects.filter(class_year=class_year, subjects=subject)

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
                    'class_work_score': str(score.class_work_score),  # Include all relevant score fields
                    'progressive_test_1_score': str(score.progressive_test_1_score),
                    'progressive_test_2_score': str(score.progressive_test_2_score),
                    'progressive_test_3_score': str(score.progressive_test_3_score),
                    'midterm_score': str(score.midterm_score),
                    'exam_score': str(score.exam_score),
                    'continuous_assessment': str(score.continuous_assessment),
                    'total_score': str(score.total_score),
                    'grade': score.grade
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


# Fucntion to delete scores from the database 
@login_required(login_url='login')
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


# Fetch that generates reports
@login_required(login_url='login')
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

            # Fetch all scores for the student in the selected term (regardless of the user who created them)
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
                'report_data': scores,  # Pass the scores directly
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


@login_required(login_url='login')
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


# def calculate_gpa(scores):
#     """
#     Calculate the GPA from a list of scores using a proportional scale.
#     If the total score is 100, GPA is 4.0, and if the total score is 0, GPA is 0.0.
#     The GPA is calculated proportionally for other scores.
#     """
#     total_points = 0
#     total_subjects = len(scores)
    
#     if total_subjects == 0:
#         print("No scores available to calculate GPA.")
#         return 0.0

#     # Iterate over each score and calculate GPA based on total_score
#     for score in scores:
#         try:
#             # Get the total score from the Score object
#             total_score = Decimal(score.total_score)

#             # GPA calculation based on total_score (0 to 100 scale)
#             gpa = (total_score / Decimal(100)) * Decimal(4.0)
            
#             # Add the calculated GPA to the total points
#             total_points += gpa

#         except Exception as e:
#             # If there's an error, log it and skip this score
#             print(f"Error calculating GPA for score {score}: {e}")
#             total_points += 0  # Add 0 in case of error

#     # Return the GPA rounded to two decimal places
#     final_gpa = round(total_points / total_subjects, 2) if total_subjects > 0 else 0.0
#     print(f"Final GPA: {final_gpa}")
#     return final_gpa


def calculate_gpa(scores):
    """
    Calculate the GPA from a list of scores based on fixed grade ranges.
    The GPA points are assigned as per the following scale:
    A* 95% - 100% -> GPA: 4.00
    A 80% - 94% -> GPA: 3.67
    B+ 75% - 79% -> GPA: 3.33
    B 70% - 74% -> GPA: 3.00
    C+ 65% - 69% -> GPA: 2.67
    C 60% - 64% -> GPA: 2.33
    D 50% - 59% -> GPA: 2.00
    E 45% - 49% -> GPA: 1.67
    F 35% - 44% -> GPA: 1.00
    Ungraded 0% - 34% -> GPA: 0.00
    """
    total_points = 0
    total_subjects = len(scores)
    
    if total_subjects == 0:
        print("No scores available to calculate GPA.")
        return 0.0

    # Define GPA mappings for different score ranges
    def get_gpa_for_score(total_score):
        if 95 <= total_score <= 100:
            return 4.00  # A*
        elif 80 <= total_score < 95:
            return 3.67  # A
        elif 75 <= total_score < 80:
            return 3.33  # B+
        elif 70 <= total_score < 75:
            return 3.00  # B
        elif 65 <= total_score < 70:
            return 2.67  # C+
        elif 60 <= total_score < 65:
            return 2.33  # C
        elif 50 <= total_score < 60:
            return 2.00  # D
        elif 45 <= total_score < 50:
            return 1.67  # E
        elif 35 <= total_score < 45:
            return 1.00  # F
        else:
            return 0.00  # Ungraded

    # Iterate over each score and calculate GPA based on the total_score
    for score in scores:
        try:
            # Get the total score from the Score object
            total_score = Decimal(score.total_score)

            # Assign GPA based on total_score using the defined scale
            gpa = get_gpa_for_score(total_score)

            # Add the calculated GPA to the total points
            total_points += gpa

        except Exception as e:
            # If there's an error, log it and skip this score
            print(f"Error calculating GPA for score {score}: {e}")
            total_points += 0  # Add 0 in case of error

    # Return the GPA rounded to two decimal places
    final_gpa = round(total_points / total_subjects, 2) if total_subjects > 0 else 0.0
    print(f"Final GPA: {final_gpa}")
    return final_gpa
