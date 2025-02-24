from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .models import (
    Level, ClassYear, 
    Term, Subject, Student, TeacherProfile,
    Score, AcademicReport,MidtermReport,
    ProgressiveTestOneReport,ProgressiveTestTwoReport,
    ProgressiveTestThreeReport
)
from django.shortcuts import render
from django.template.loader import render_to_string
from decimal import Decimal 
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from reports.utils import calculate_gpa


#==================== Login View ====================
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


#==================== Select Option View  ====================
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



#============ Process Class Scores View ================
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
        'students': Student.objects.all(),
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

                    # Update or create the score instance and save
                    score_instance, created = Score.objects.update_or_create(
                        student=student,
                        term=term,
                        subject=subject,
                        created_by=request.user,
                        defaults={'midterm_score': midterm_score}
                    )

                    # No need to call score_instance.save() as update_or_create will trigger the save.

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



##=============== Logic for processing and display the saved end of term scores for the user ===============
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




# Functional Logic to fetch all end of term scores :
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



# Functional Logic to fetch all midterm test scores :
def view_midterm_report(request, student_id, term_id):
    try:
        student = Student.objects.get(id=student_id)
        scores = Score.objects.filter(student=student, term=term_id).distinct('subject')
        term = get_object_or_404(Term, id=term_id)
        
        # Ensure that class_year is serialized to a string or relevant field
        class_year = student.class_year.name if hasattr(student.class_year, 'name') else str(student.class_year)

        # Function to calculate grade based on progressive_test_1_score
        def get_grade_from_midterm_score(score):
            if score >= 95 and score <= 100:
                return 'A*'  # Grade for 95% - 100%
            elif score >= 80 and score < 95:
                return 'A'  # Grade for 80% - 94%
            elif score >= 75 and score < 80:
                return 'B+'  # Grade for 75% - 79%
            elif score >= 70 and score < 75:
                return 'B'  # Grade for 70% - 74%
            elif score >= 65 and score < 70:
                return 'C+'  # Grade for 65% - 69%
            elif score >= 60 and score < 65:
                return 'C'  # Grade for 60% - 64%
            elif score >= 50 and score < 60:
                return 'D'  # Grade for 50% - 59%
            elif score >= 45 and score < 50:
                return 'E'  # Grade for 45% - 49%
            elif score >= 35 and score < 45:
                return 'F'  # Grade for 35% - 44%
            else:
                return 'Ungraded'  # Grade for 0% - 34%

        # Function to calculate GPA based on a score
        def get_gpa_from_midterm_score(score):
            if score >= 95 and score <= 100:
                return 4.00
            elif score >= 80 and score < 95:
                return 3.67
            elif score >= 75 and score < 80:
                return 3.33
            elif score >= 70 and score < 75:
                return 3.00
            elif score >= 65 and score < 70:
                return 2.67
            elif score >= 60 and score < 65:
                return 2.33
            elif score >= 50 and score < 60:
                return 2.00
            elif score >= 45 and score < 50:
                return 1.67
            elif score >= 35 and score < 45:
                return 1.00
            else:
                return 0.00

        # Calculate total score percentage as float to avoid decimal.Decimal issues
        if scores.exists():
            total_score = sum([score.midterm_score for score in scores])
            total_score_percentage = float(total_score) / (len(scores) * 100) * 100  # Cast to float
        else:
            total_score_percentage = 0.0  # If no scores exist, default to 0%

        # Calculate GPA based on total score percentage
        total_gpa = get_gpa_from_midterm_score(total_score_percentage)

        # Prepare data to be returned in the JSON response
        midterm_report = {
            'student_name': student.fullname,
            'class_year': class_year,  # Ensure it's a serializable value (e.g., string)
            'term': term.term_name,
            'total_score_percentage': total_score_percentage,
            'total_gpa': total_gpa,  # Add the total GPA
            'scores': [
                {
                    'subject': score.subject.name,
                    'midterm_score': score.midterm_score,
                    'grade': get_grade_from_midterm_score(score.midterm_score),  # Grade based on progressive test score
                    'gpa': get_gpa_from_midterm_score(score.midterm_score)  # GPA based on individual score
                }
                for score in scores
            ]
        }

        # Return a JsonResponse with the midterm report data
        return JsonResponse(midterm_report)

    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# # Functional Logic to fetch all progressive test one scores :
@login_required(login_url='login')
def view_progressive_test_score_one_report(request, student_id, term_id):
    try:
        student = Student.objects.get(id=student_id)
        scores = Score.objects.filter(student=student, term=term_id)
        term = get_object_or_404(Term, id=term_id)
        
        # Ensure that class_year is serialized to a string or relevant field
        class_year = student.class_year.name if hasattr(student.class_year, 'name') else str(student.class_year)

        # Function to calculate grade based on progressive_test_1_score
        def get_grade_from_progressive_test_score(score):
            if score >= 95 and score <= 100:
                return 'A*'
            elif score >= 80 and score < 95:
                return 'A'
            elif score >= 75 and score < 80:
                return 'B+'
            elif score >= 70 and score < 75:
                return 'B'
            elif score >= 65 and score < 70:
                return 'C+'
            elif score >= 60 and score < 65:
                return 'C'
            elif score >= 50 and score < 60:
                return 'D'
            elif score >= 45 and score < 50:
                return 'E'
            elif score >= 35 and score < 45:
                return 'F'
            else:
                return 'Ungraded'

        # Function to calculate GPA based on progressive_test_1_score
        def get_gpa_from_progressive_test_score(score):
            if score >= 95 and score <= 100:
                return Decimal(4.00)
            elif score >= 80 and score < 95:
                return Decimal(3.67)
            elif score >= 75 and score < 80:
                return Decimal(3.33)
            elif score >= 70 and score < 75:
                return Decimal(3.00)
            elif score >= 65 and score < 70:
                return Decimal(2.67)
            elif score >= 60 and score < 65:
                return Decimal(2.33)
            elif score >= 50 and score < 60:
                return Decimal(2.00)
            elif score >= 45 and score < 50:
                return Decimal(1.67)
            elif score >= 35 and score < 45:
                return Decimal(1.00)
            else:
                return Decimal(0.00)

        # Calculate total score percentage
        if scores.exists():
            total_score = sum([score.progressive_test_1_score for score in scores])
            total_score_percentage = (total_score / (len(scores) * 100)) * 100
        else:
            total_score_percentage = 0  # If no scores exist, default to 0%

        # Calculate GPA based on total score percentage
        total_gpa = get_gpa_from_progressive_test_score(total_score_percentage)

        # Prepare data to be returned in the JSON response
        progressive_test_score_one_report = {
            'student_name': student.fullname,
            'class_year': class_year,
            'term': term.term_name,
            'total_score_percentage': total_score_percentage,
            'total_gpa': float(total_gpa),  # Ensure GPA is a float for JSON serialization
            'scores': [
                {
                    'subject': score.subject.name,
                    'progressive_test_one_score': float(score.progressive_test_1_score),  # Convert Decimal to float
                    'grade': get_grade_from_progressive_test_score(score.progressive_test_1_score),
                    'gpa': float(get_gpa_from_progressive_test_score(score.progressive_test_1_score))
                }
                for score in scores
            ]
        }

        # Return a JsonResponse with the progressive_test_score_one_report data
        return JsonResponse(progressive_test_score_one_report)

    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




# Functional Logic to fetch all progressive test two scores :
@login_required(login_url='login')
def view_progressive_test_score_two_report(request, student_id, term_id):
    try:
        student = Student.objects.get(id=student_id)
        scores = Score.objects.filter(student=student, term=term_id)
        term = get_object_or_404(Term, id=term_id)
        
        # Ensure that class_year is serialized to a string or relevant field
        class_year = student.class_year.name if hasattr(student.class_year, 'name') else str(student.class_year)

        # Function to calculate grade based on progressive_test_1_score
        def get_grade_from_progressive_test_score(score):
            if score >= 95 and score <= 100:
                return 'A*'  # Grade for 95% - 100%
            elif score >= 80 and score < 95:
                return 'A'  # Grade for 80% - 94%
            elif score >= 75 and score < 80:
                return 'B+'  # Grade for 75% - 79%
            elif score >= 70 and score < 75:
                return 'B'  # Grade for 70% - 74%
            elif score >= 65 and score < 70:
                return 'C+'  # Grade for 65% - 69%
            elif score >= 60 and score < 65:
                return 'C'  # Grade for 60% - 64%
            elif score >= 50 and score < 60:
                return 'D'  # Grade for 50% - 59%
            elif score >= 45 and score < 50:
                return 'E'  # Grade for 45% - 49%
            elif score >= 35 and score < 45:
                return 'F'  # Grade for 35% - 44%
            else:
                return 'Ungraded'  # Grade for 0% - 34%

        # Function to calculate GPA based on a score
        def get_gpa_from_progressive_test_score(score):
            if score >= 95 and score <= 100:
                return 4.00
            elif score >= 80 and score < 95:
                return 3.67
            elif score >= 75 and score < 80:
                return 3.33
            elif score >= 70 and score < 75:
                return 3.00
            elif score >= 65 and score < 70:
                return 2.67
            elif score >= 60 and score < 65:
                return 2.33
            elif score >= 50 and score < 60:
                return 2.00
            elif score >= 45 and score < 50:
                return 1.67
            elif score >= 35 and score < 45:
                return 1.00
            else:
                return 0.00

        # Calculate total score percentage
        if scores.exists():
            total_score = sum([score.progressive_test_2_score for score in scores])
            total_score_percentage = (total_score / (len(scores) * 100)) * 100
        else:
            total_score_percentage = 0  # If no scores exist, default to 0%

        # Calculate GPA based on total score percentage
        total_gpa = get_gpa_from_progressive_test_score(total_score_percentage)

        # Prepare data to be returned in the JSON response
        progressive_test_score_two_report = {
            'student_name': student.fullname,
            'class_year': class_year,  # Ensure it's a serializable value (e.g., string)
            'term': term.term_name,
            'total_score_percentage': total_score_percentage,
            'total_gpa': total_gpa,  # Add the total GPA
            'scores': [
                {
                    'subject': score.subject.name,
                    'progressive_test_one_score': score.progressive_test_2_score,
                    'grade': get_grade_from_progressive_test_score(score.progressive_test_2_score),  # Grade based on progressive test score
                    'gpa': get_gpa_from_progressive_test_score(score.progressive_test_2_score)  # GPA based on individual score
                }
                for score in scores
            ]
        }

        # Return a JsonResponse with the progressive_test_score_one_report data
        return JsonResponse(progressive_test_score_two_report)

    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




# Functional Logic to fetch all progressive test three scores :
@login_required(login_url='login')
def view_progressive_test_score_three_report(request, student_id, term_id):
    try:
        student = Student.objects.get(id=student_id)
        scores = Score.objects.filter(student=student, term=term_id)
        term = get_object_or_404(Term, id=term_id)
        
        # Ensure that class_year is serialized to a string or relevant field
        class_year = student.class_year.name if hasattr(student.class_year, 'name') else str(student.class_year)

        # Function to calculate grade based on progressive_test_1_score
        def get_grade_from_progressive_test_score(score):
            if score >= 95 and score <= 100:
                return 'A*'  # Grade for 95% - 100%
            elif score >= 80 and score < 95:
                return 'A'  # Grade for 80% - 94%
            elif score >= 75 and score < 80:
                return 'B+'  # Grade for 75% - 79%
            elif score >= 70 and score < 75:
                return 'B'  # Grade for 70% - 74%
            elif score >= 65 and score < 70:
                return 'C+'  # Grade for 65% - 69%
            elif score >= 60 and score < 65:
                return 'C'  # Grade for 60% - 64%
            elif score >= 50 and score < 60:
                return 'D'  # Grade for 50% - 59%
            elif score >= 45 and score < 50:
                return 'E'  # Grade for 45% - 49%
            elif score >= 35 and score < 45:
                return 'F'  # Grade for 35% - 44%
            else:
                return 'Ungraded'  # Grade for 0% - 34%

        # Function to calculate GPA based on a score
        def get_gpa_from_progressive_test_score(score):
            if score >= 95 and score <= 100:
                return 4.00
            elif score >= 80 and score < 95:
                return 3.67
            elif score >= 75 and score < 80:
                return 3.33
            elif score >= 70 and score < 75:
                return 3.00
            elif score >= 65 and score < 70:
                return 2.67
            elif score >= 60 and score < 65:
                return 2.33
            elif score >= 50 and score < 60:
                return 2.00
            elif score >= 45 and score < 50:
                return 1.67
            elif score >= 35 and score < 45:
                return 1.00
            else:
                return 0.00

        # Calculate total score percentage
        if scores.exists():
            total_score = sum([score.progressive_test_3_score for score in scores])
            total_score_percentage = (total_score / (len(scores) * 100)) * 100
        else:
            total_score_percentage = 0  # If no scores exist, default to 0%

        # Calculate GPA based on total score percentage
        total_gpa = get_gpa_from_progressive_test_score(total_score_percentage)

        # Prepare data to be returned in the JSON response
        progressive_test_score_three_report = {
            'student_name': student.fullname,
            'class_year': class_year,  # Ensure it's a serializable value (e.g., string)
            'term': term.term_name,
            'total_score_percentage': total_score_percentage,
            'total_gpa': total_gpa,  # Add the total GPA
            'scores': [
                {
                    'subject': score.subject.name,
                    'progressive_test_one_score': score.progressive_test_3_score,
                    'grade': get_grade_from_progressive_test_score(score.progressive_test_3_score),  # Grade based on progressive test score
                    'gpa': get_gpa_from_progressive_test_score(score.progressive_test_3_score)  # GPA based on individual score
                }
                for score in scores
            ]
        }

        # Return a JsonResponse with the progressive_test_score_one_report data
        return JsonResponse(progressive_test_score_three_report)

    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



# Functional Logic to dunamically fetch the various levels :
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

        # Get the TeacherProfile for the logged-in user
        teacher_profile = TeacherProfile.objects.get(user=request.user)

        # Filter subjects by both class year and teacher's subjects
        subjects = Subject.objects.filter(class_year=class_year, id__in=teacher_profile.subjects.values_list('id', flat=True))
        
        # Serialize the subjects into a list of dictionaries
        subjects_data = [{'id': subject.id, 'name': subject.name} for subject in subjects]

        return JsonResponse({'subjects': subjects_data})
    
    except ClassYear.DoesNotExist:
        return JsonResponse({'error': 'Class Year not found'}, status=404)
    except TeacherProfile.DoesNotExist:
        return JsonResponse({'error': 'Teacher Profile not found'}, status=404)




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

        print(f"Request received: student_name={student_name}, class_year={class_year}, term_name={term_name}")

        try:
            # Fetch the student, class_year, and term objects
            student = Student.objects.get(fullname=student_name)
            class_year_obj = ClassYear.objects.get(name=class_year)
            term = Term.objects.get(term_name=term_name, class_year=class_year_obj)

            print(f"Fetched: student={student.fullname}, class_year={class_year_obj.name}, term={term.term_name}")

            # Fetch all scores for the student in the selected term
            scores = Score.objects.filter(student=student, term=term).distinct('subject')
            print(f"Fetched scores: {len(scores)} scores found for student {student_name} in term {term_name}")

            if not scores.exists():
                print(f"No scores found for {student_name} in term {term_name}")
                return JsonResponse({
                    'success': False,
                    'error': f'No scores found for {student_name} in {term_name}.'
                })

            # Create or update the AcademicReport instance for this student and term
            academic_report, created = AcademicReport.objects.get_or_create(
                student=student,
                term=term
            )

            if created:
                print(f"New AcademicReport created for {student_name} - {term_name}")
                academic_report.student_scores.set(scores)  # Assign the scores to the report

            # Save the academic report which will trigger GPA calculation
            academic_report.save()  # The GPA will be automatically calculated by the model's save method
            print(f"Academic report saved with ID: {academic_report.id} and GPA: {academic_report.student_gpa}")

            # Render the HTML for the report using the 'generated_report.html' template
            report_html = render_to_string('generated_report.html', {
                'student_name': student_name,
                'class_year': class_year,
                'term_name': term_name,
                'gpa': academic_report.student_gpa,
                'report_data': scores,  # Pass the scores directly
            })

            print(f"Report HTML generated successfully.")

            # Return the HTML content in the JSON response
            return JsonResponse({
                'success': True,
                'report_html': report_html  # Pass the generated HTML content
            })

        except Student.DoesNotExist:
            print(f"Error: Student {student_name} not found.")
            return JsonResponse({'success': False, 'error': 'Student not found.'})
        except Term.DoesNotExist:
            print(f"Error: Term {term_name} not found.")
            return JsonResponse({'success': False, 'error': 'Term not found.'})
        except ClassYear.DoesNotExist:
            print(f"Error: Class Year {class_year} not found.")
            return JsonResponse({'success': False, 'error': 'Class Year not found.'})
        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})




# This logic allows me to generate midterm reports dynamically
@login_required(login_url='login')
def generate_midterm_report(request):
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

            # Fetch all scores for the student in the selected term
            scores = Score.objects.filter(student=student, term=term).distinct('subject')

            # Function to calculate grade based on midterm_score
            def get_grade_from_midterm_score(score):
                if score >= 95 and score <= 100:
                    return 'A*'
                elif score >= 80 and score < 95:
                    return 'A'
                elif score >= 75 and score < 80:
                    return 'B+'
                elif score >= 70 and score < 75:
                    return 'B'
                elif score >= 65 and score < 70:
                    return 'C+'
                elif score >= 60 and score < 65:
                    return 'C'
                elif score >= 50 and score < 60:
                    return 'D'
                elif score >= 45 and score < 50:
                    return 'E'
                elif score >= 35 and score < 45:
                    return 'F'
                else:
                    return 'Ungraded'

            # Function to calculate GPA based on midterm_score
            def get_gpa_from_midterm_score(score):
                if score >= 95 and score <= 100:
                    return 4.00
                elif score >= 80 and score < 95:
                    return 3.67
                elif score >= 75 and score < 80:
                    return 3.33
                elif score >= 70 and score < 75:
                    return 3.00
                elif score >= 65 and score < 70:
                    return 2.67
                elif score >= 60 and score < 65:
                    return 2.33
                elif score >= 50 and score < 60:
                    return 2.00
                elif score >= 45 and score < 50:
                    return 1.67
                elif score >= 35 and score < 45:
                    return 1.00
                else:
                    return 0.00

            # Calculate total score percentage and GPA
            if scores.exists():
                total_score = sum([score.midterm_score for score in scores])
                total_score_percentage = (total_score / (len(scores) * 100)) * 100
            else:
                total_score_percentage = 0  # If no scores exist, default to 0%

            # Calculate GPA based on total score percentage
            total_gpa = get_gpa_from_midterm_score(total_score_percentage)

            # Create or update the MidtermReport instance for this student and term
            midterm_report, created = MidtermReport.objects.get_or_create(
                student=student,
                term=term
            )

            # If it's a new report, set the fields and save
            if created:
                # Set the necessary fields for the new report
                midterm_report.student = student
                midterm_report.term = term
                midterm_report.midterm_gpa = float(total_gpa)
                midterm_report.generated_by = request.user  # Automatically set generated_by to the current user

                # Save the report first to generate an ID
                midterm_report.save()

                # Set the scores to the MidtermReport (many-to-many relationship)
                midterm_report.student_scores.set(scores)  # Set the full Score instances to the report

                # Save again after assigning the many-to-many relationship
                midterm_report.save()

            # Prepare data to be returned in the JSON response
            midterm_report_data = {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,  # Ensure it's a serializable value (e.g., string)
                'term': term.term_name,
                'total_score_percentage': total_score_percentage,
                'total_gpa': total_gpa,  # Add the total GPA
                'scores': [
                    {
                        'subject': score.subject.name,
                        'midterm_score': score.midterm_score,
                        'grade': get_grade_from_midterm_score(score.midterm_score),
                        'gpa': get_gpa_from_midterm_score(score.midterm_score)
                    }
                    for score in scores
                ]
            }

            # Render the HTML for the report using the 'generated_report.html' template
            report_html = render_to_string('generated_midterm_report.html', {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,
                'term_name': term.term_name,
                'gpa': total_gpa,
                'report_data': midterm_report_data['scores'],  # Pass the scores directly
            })

            # Return a JsonResponse with the generated report data
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


# This logic allows me to generate progressive tests one reports dynamically
@login_required(login_url='login')
def generate_progressive_one_report(request):
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

            # Fetch all scores for the student in the selected term
            scores = Score.objects.filter(student=student, term=term).distinct('subject')

            # Function to calculate grade based on progressive_test_1_score
            def get_grade_from_progressive_test_1_score(score):
                if score >= 95 and score <= 100:
                    return 'A*'
                elif score >= 80 and score < 95:
                    return 'A'
                elif score >= 75 and score < 80:
                    return 'B+'
                elif score >= 70 and score < 75:
                    return 'B'
                elif score >= 65 and score < 70:
                    return 'C+'
                elif score >= 60 and score < 65:
                    return 'C'
                elif score >= 50 and score < 60:
                    return 'D'
                elif score >= 45 and score < 50:
                    return 'E'
                elif score >= 35 and score < 45:
                    return 'F'
                else:
                    return 'Ungraded'

            # Function to calculate GPA based on progressive_test_1_score
            def get_gpa_from_progressive_test_1_score(score):
                if score >= 95 and score <= 100:
                    return 4.00
                elif score >= 80 and score < 95:
                    return 3.67
                elif score >= 75 and score < 80:
                    return 3.33
                elif score >= 70 and score < 75:
                    return 3.00
                elif score >= 65 and score < 70:
                    return 2.67
                elif score >= 60 and score < 65:
                    return 2.33
                elif score >= 50 and score < 60:
                    return 2.00
                elif score >= 45 and score < 50:
                    return 1.67
                elif score >= 35 and score < 45:
                    return 1.00
                else:
                    return 0.00

            # Calculate total score percentage and GPA
            if scores.exists():
                total_score = sum([score.progressive_test_1_score for score in scores if score.progressive_test_1_score is not None])
                total_score_percentage = (total_score / (len(scores) * 100)) * 100 if len(scores) > 0 else 0
            else:
                total_score_percentage = 0  # If no scores exist, default to 0%

            # Calculate GPA based on total score percentage
            total_gpa = get_gpa_from_progressive_test_1_score(total_score_percentage)

            # Create or update the ProgressiveReport instance for this student and term
            progressive_report, created = ProgressiveTestOneReport.objects.get_or_create(
                student=student,
                term=term
            )

            # If it's a new report, set the fields and save
            if created:
                # Set the necessary fields for the new report
                progressive_report.student = student
                progressive_report.term = term
                progressive_report.progressive_test_1_gpa = float(total_gpa)
                progressive_report.generated_by = request.user  # Automatically set generated_by to the current user

                # Save the report first to generate an ID
                progressive_report.save()

                # Set the scores to the ProgressiveReport (many-to-many relationship)
                progressive_report.student_scores.set(scores)  # Set the full Score instances to the report

                # Save again after assigning the many-to-many relationship
                progressive_report.save()

            # Prepare data to be returned in the JSON response
            progressive_report_data = {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,  # Ensure it's a serializable value (e.g., string)
                'term': term.term_name,
                'total_score_percentage': total_score_percentage,
                'total_gpa': total_gpa,  # Add the total GPA
                'scores': [
                    {
                        'subject': score.subject.name,
                        'progressive_test_1_score': score.progressive_test_1_score,
                        'grade': get_grade_from_progressive_test_1_score(score.progressive_test_1_score),
                        'gpa': get_gpa_from_progressive_test_1_score(score.progressive_test_1_score)
                    }
                    for score in scores
                ]
            }

            # Render the HTML for the report using the 'generated_progressive_report.html' template
            report_html = render_to_string('generated_progressive_test_one_report.html', {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,
                'term_name': term.term_name,
                'gpa': total_gpa,
                'report_data': progressive_report_data['scores'],  # Pass the scores directly
            })

            # Return a JsonResponse with the generated report data
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
def generate_progressive_two_report(request):
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

            # Fetch all scores for the student in the selected term
            scores = Score.objects.filter(student=student, term=term).distinct('subject')

            # Function to calculate grade based on progressive_test_2_score
            def get_grade_from_progressive_test_2_score(score):
                if score >= 95 and score <= 100:
                    return 'A*'
                elif score >= 80 and score < 95:
                    return 'A'
                elif score >= 75 and score < 80:
                    return 'B+'
                elif score >= 70 and score < 75:
                    return 'B'
                elif score >= 65 and score < 70:
                    return 'C+'
                elif score >= 60 and score < 65:
                    return 'C'
                elif score >= 50 and score < 60:
                    return 'D'
                elif score >= 45 and score < 50:
                    return 'E'
                elif score >= 35 and score < 45:
                    return 'F'
                else:
                    return 'Ungraded'

            # Function to calculate GPA based on progressive_test_2_score
            def get_gpa_from_progressive_test_2_score(score):
                if score >= 95 and score <= 100:
                    return 4.00
                elif score >= 80 and score < 95:
                    return 3.67
                elif score >= 75 and score < 80:
                    return 3.33
                elif score >= 70 and score < 75:
                    return 3.00
                elif score >= 65 and score < 70:
                    return 2.67
                elif score >= 60 and score < 65:
                    return 2.33
                elif score >= 50 and score < 60:
                    return 2.00
                elif score >= 45 and score < 50:
                    return 1.67
                elif score >= 35 and score < 45:
                    return 1.00
                else:
                    return 0.00

            # Calculate total score percentage and GPA
            if scores.exists():
                total_score = sum([score.progressive_test_2_score for score in scores if score.progressive_test_2_score is not None])
                total_score_percentage = (total_score / (len(scores) * 100)) * 100 if len(scores) > 0 else 0
            else:
                total_score_percentage = 0  # If no scores exist, default to 0%

            # Calculate GPA based on total score percentage
            total_gpa = get_gpa_from_progressive_test_2_score(total_score_percentage)

            # Create or update the ProgressiveReport instance for this student and term
            progressive_report, created = ProgressiveTestTwoReport.objects.get_or_create(
                student=student,
                term=term
            )

            # If it's a new report, set the fields and save
            if created:
                # Set the necessary fields for the new report
                progressive_report.student = student
                progressive_report.term = term
                progressive_report.progressive_test2_gpa = float(total_gpa)
                progressive_report.generated_by = request.user  # Automatically set generated_by to the current user

                # Save the report first to generate an ID
                progressive_report.save()

                # Set the scores to the ProgressiveReport (many-to-many relationship)
                progressive_report.student_scores.set(scores)  # Set the full Score instances to the report

                # Save again after assigning the many-to-many relationship
                progressive_report.save()

            # Prepare data to be returned in the JSON response
            progressive_report_data = {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,  # Ensure it's a serializable value (e.g., string)
                'term': term.term_name,
                'total_score_percentage': total_score_percentage,
                'total_gpa': total_gpa,  # Add the total GPA
                'scores': [
                    {
                        'subject': score.subject.name,
                        'progressive_test_2_score': score.progressive_test_2_score,
                        'grade': get_grade_from_progressive_test_2_score(score.progressive_test_2_score),
                        'gpa': get_gpa_from_progressive_test_2_score(score.progressive_test_2_score)
                    }
                    for score in scores
                ]
            }

            # Render the HTML for the report using the 'generated_progressive_test_two_report.html' template
            report_html = render_to_string('generated_progressive_test_two_report.html', {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,
                'term_name': term.term_name,
                'gpa': total_gpa,
                'report_data': progressive_report_data['scores'],  # Pass the scores directly
            })

            # Return a JsonResponse with the generated report data
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
def generate_progressive_three_report(request):
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

            # Fetch all scores for the student in the selected term
            scores = Score.objects.filter(student=student, term=term).distinct('subject')

            # Function to calculate grade based on progressive_test_3_score
            def get_grade_from_progressive_test_3_score(score):
                if score >= 95 and score <= 100:
                    return 'A*'
                elif score >= 80 and score < 95:
                    return 'A'
                elif score >= 75 and score < 80:
                    return 'B+'
                elif score >= 70 and score < 75:
                    return 'B'
                elif score >= 65 and score < 70:
                    return 'C+'
                elif score >= 60 and score < 65:
                    return 'C'
                elif score >= 50 and score < 60:
                    return 'D'
                elif score >= 45 and score < 50:
                    return 'E'
                elif score >= 35 and score < 45:
                    return 'F'
                else:
                    return 'Ungraded'

            # Function to calculate GPA based on progressive_test_3_score
            def get_gpa_from_progressive_test_3_score(score):
                if score >= 95 and score <= 100:
                    return 4.00
                elif score >= 80 and score < 95:
                    return 3.67
                elif score >= 75 and score < 80:
                    return 3.33
                elif score >= 70 and score < 75:
                    return 3.00
                elif score >= 65 and score < 70:
                    return 2.67
                elif score >= 60 and score < 65:
                    return 2.33
                elif score >= 50 and score < 60:
                    return 2.00
                elif score >= 45 and score < 50:
                    return 1.67
                elif score >= 35 and score < 45:
                    return 1.00
                else:
                    return 0.00

            # Calculate total score percentage and GPA
            if scores.exists():
                total_score = sum([score.progressive_test_3_score for score in scores if score.progressive_test_3_score is not None])
                total_score_percentage = (total_score / (len(scores) * 100)) * 100 if len(scores) > 0 else 0
            else:
                total_score_percentage = 0  # If no scores exist, default to 0%

            # Calculate GPA based on total score percentage
            total_gpa = get_gpa_from_progressive_test_3_score(total_score_percentage)

            # Create or update the ProgressiveReport instance for this student and term
            progressive_report, created = ProgressiveTestThreeReport.objects.get_or_create(
                student=student,
                term=term
            )

            # If it's a new report, set the fields and save
            if created:
                # Set the necessary fields for the new report
                progressive_report.student = student
                progressive_report.term = term
                progressive_report.progressive_test3_gpa = float(total_gpa)
                progressive_report.generated_by = request.user  # Automatically set generated_by to the current user

                # Save the report first to generate an ID
                progressive_report.save()

                # Set the scores to the ProgressiveReport (many-to-many relationship)
                progressive_report.student_scores.set(scores)  # Set the full Score instances to the report

                # Save again after assigning the many-to-many relationship
                progressive_report.save()

            # Prepare data to be returned in the JSON response
            progressive_report_data = {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,  # Ensure it's a serializable value (e.g., string)
                'term': term.term_name,
                'total_score_percentage': total_score_percentage,
                'total_gpa': total_gpa,  # Add the total GPA
                'scores': [
                    {
                        'subject': score.subject.name,
                        'progressive_test_3_score': score.progressive_test_3_score,
                        'grade': get_grade_from_progressive_test_3_score(score.progressive_test_3_score),
                        'gpa': get_gpa_from_progressive_test_3_score(score.progressive_test_3_score)
                    }
                    for score in scores
                ]
            }

            # Render the HTML for the report using the 'generated_progressive_test_three_report.html' template
            report_html = render_to_string('generated_progressive_test_three_report.html', {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,
                'term_name': term.term_name,
                'gpa': total_gpa,
                'report_data': progressive_report_data['scores'],  # Pass the scores directly
            })

            # Return a JsonResponse with the generated report data
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




#=============== Logic for viewing the saved scores ===============
# Viewing Saved End of Term  Scores by Term:
@login_required(login_url='login')
def view_end_of_term_scores(request, term_id=None):
    # Ensure that term_id is provided
    if not term_id:
        return JsonResponse({'error': 'Term is required'}, status=400)

    try:
        # Fetch the term object
        term = Term.objects.get(id=term_id)

        # Fetch all scores for the selected term and the students that belong to it
        scores = Score.objects.filter(term=term)

        # Prepare a dictionary of student scores by subject
        students_data = {}

        # Function to calculate grade from total score
        def get_grade_from_total_score(total_score):
            if total_score >= 95 and total_score <= 100:
                return 'A*'
            elif total_score >= 80 and total_score < 95:
                return 'A'
            elif total_score >= 75 and total_score < 80:
                return 'B+'
            elif total_score >= 70 and total_score < 75:
                return 'B'
            elif total_score >= 65 and total_score < 70:
                return 'C+'
            elif total_score >= 60 and total_score < 65:
                return 'C'
            elif total_score >= 50 and total_score < 60:
                return 'D'
            elif total_score >= 45 and total_score < 50:
                return 'E'
            elif total_score >= 35 and total_score < 45:
                return 'F'
            else:
                return 'Ungraded'

        # Function to calculate GPA from total score
        def get_gpa_from_total_score(total_score):
            if total_score >= 95 and total_score <= 100:
                return 4.00
            elif total_score >= 80 and total_score < 95:
                return 3.67
            elif total_score >= 75 and total_score < 80:
                return 3.33
            elif total_score >= 70 and total_score < 75:
                return 3.00
            elif total_score >= 65 and total_score < 70:
                return 2.67
            elif total_score >= 60 and total_score < 65:
                return 2.33
            elif total_score >= 50 and total_score < 60:
                return 2.00
            elif total_score >= 45 and total_score < 50:
                return 1.67
            elif total_score >= 35 and total_score < 45:
                return 1.00
            else:
                return 0.00

        # Loop over the scores to populate students_data
        for score in scores:
            student_id = score.student.id

            if student_id not in students_data:
                students_data[student_id] = {
                    'student_name': score.student.fullname,
                    'student_id': score.student.id,
                    'class_year': score.student.class_year.name,  # Assuming class_year is a related field
                    'scores': [],
                    'total_score': 0,
                    'final_gpa': 0,
                }

            # Calculate the total score for the student based on individual components
            continuous_assessment = (
                score.class_work_score +
                score.progressive_test_1_score +
                score.progressive_test_2_score +
                score.progressive_test_3_score +
                score.midterm_score
            )

            # Normalize continuous assessment to a 100% scale (total is out of 500, so divide by 500 and multiply by 100)
            normalized_continuous_assessment = (continuous_assessment / Decimal('500')) * Decimal('100')

            # Total score is based on 30% continuous assessment and 70% exam score
            total_score = (normalized_continuous_assessment * Decimal('0.30')) + (score.exam_score * Decimal('0.70'))

            # Assign grade based on the total_score with the new grading scale
            grade = get_grade_from_total_score(total_score)
            score_gpa = get_gpa_from_total_score(total_score)

            # Add the score details for each student and subject
            students_data[student_id]['scores'].append({
                'subject_name': score.subject.name,
                'total_score': total_score,
                'grade': grade,
                'score_gpa': score_gpa,
                'score_id': score.id
            })

            # Accumulate the total score and GPA for the student
            students_data[student_id]['total_score'] += total_score
            students_data[student_id]['final_gpa'] += score_gpa

        # After populating data, calculate final grade and final GPA
        for student_id, data in students_data.items():
            total_score = data['total_score']
            data['final_grade'] = get_grade_from_total_score(total_score)
            data['final_gpa'] = data['final_gpa']  # Final GPA is accumulated GPA across all subjects

        # Include term in the JSON response
        students_list = list(students_data.values())

        return JsonResponse({
            'students': students_list,
            'term': term.term_name,
            "term_id": term.id,
        })

    except Term.DoesNotExist:
        return JsonResponse({'error': 'Invalid term provided'}, status=404)





# Viewing Saved Midterm Scores by Term:
@login_required(login_url='login')
def view_midterm_scores(request, term_id=None):
    # Ensure that term_id is provided
    if not term_id:
        return JsonResponse({'error': 'Term is required'}, status=400)

    try:
        # Fetch the term object
        term = Term.objects.get(id=term_id)

        # Fetch all scores for the selected term and the students that belong to it
        scores = Score.objects.filter(term=term).distinct('subject')

        # Prepare a dictionary of student scores by subject
        students_data = {}

        # Function to calculate grade from total midterm score
        def get_grade_from_total_score(total_score):
            if total_score >= 95 and total_score <= 100:
                return 'A*'
            elif total_score >= 80 and total_score < 95:
                return 'A'
            elif total_score >= 75 and total_score < 80:
                return 'B+'
            elif total_score >= 70 and total_score < 75:
                return 'B'
            elif total_score >= 65 and total_score < 70:
                return 'C+'
            elif total_score >= 60 and total_score < 65:
                return 'C'
            elif total_score >= 50 and total_score < 60:
                return 'D'
            elif total_score >= 45 and total_score < 50:
                return 'E'
            elif total_score >= 35 and total_score < 45:
                return 'F'
            else:
                return 'Ungraded'

        # Function to calculate GPA from total midterm score
        def get_gpa_from_total_score(total_score):
            if total_score >= 95 and total_score <= 100:
                return 4.00
            elif total_score >= 80 and total_score < 95:
                return 3.67
            elif total_score >= 75 and total_score < 80:
                return 3.33
            elif total_score >= 70 and total_score < 75:
                return 3.00
            elif total_score >= 65 and total_score < 70:
                return 2.67
            elif total_score >= 60 and total_score < 65:
                return 2.33
            elif total_score >= 50 and total_score < 60:
                return 2.00
            elif total_score >= 45 and total_score < 50:
                return 1.67
            elif total_score >= 35 and total_score < 45:
                return 1.00
            else:
                return 0.00

        # Loop over the scores to populate students_data
        for score in scores:
            student_id = score.student.id
            subject_name = score.subject.name

            if student_id not in students_data:
                students_data[student_id] = {
                    'student_name': score.student.fullname,
                    'student_id': score.student.id,
                    'class_year': score.student.class_year.name,  # Assuming class_year is a related field
                    'scores': [],
                    'total_score': 0,
                    'final_gpa': 0,
                }

            # Add the score details for each student and subject
            score_gpa = get_gpa_from_total_score(score.midterm_score)
            grade = get_grade_from_total_score(score.midterm_score)

            students_data[student_id]['scores'].append({
                'subject_name': subject_name,
                'midterm_score': score.midterm_score,
                'score_gpa': score_gpa,
                'grade': grade,
                'score_id': score.id
            })

            # Accumulate the total score and GPA for the student
            students_data[student_id]['total_score'] += score.midterm_score
            students_data[student_id]['final_gpa'] += score_gpa

        # After populating data, calculate final grade and final GPA
        for student_id, data in students_data.items():
            total_score = data['total_score']
            total_score_percentage = total_score  # We can directly use total_score here

            data['final_gpa'] = data['final_gpa']  # Final GPA is accumulated GPA across all subjects

        # Include term in the JSON response
        students_list = list(students_data.values())

        return JsonResponse({
            'students': students_list,
            'term': term.term_name,
            "term_id":term.id,
        })

    except Term.DoesNotExist:
        return JsonResponse({'error': 'Invalid term provided'}, status=404)




# Viewing Saved Progressive Test One Scores by Term:
@login_required(login_url='login')
def view_progressive_one_test_scores(request, term_id=None):
    # Ensure that term_id is provided
    if not term_id:
        return JsonResponse({'error': 'Term is required'}, status=400)
    try:
        # Fetch the term object
        term = Term.objects.get(id=term_id)

        # Fetch all scores for the selected term and the students that belong to it
        scores = Score.objects.filter(term=term)

        # Prepare a dictionary to store the student data
        students_data = {}

        # Function to calculate grade from progressive_test_1_score
        def get_grade_from_progressive_score(score):
            if score >= 95 and score <= 100:
                return 'A*'
            elif score >= 80 and score < 95:
                return 'A'
            elif score >= 75 and score < 80:
                return 'B+'
            elif score >= 70 and score < 75:
                return 'B'
            elif score >= 65 and score < 70:
                return 'C+'
            elif score >= 60 and score < 65:
                return 'C'
            elif score >= 50 and score < 60:
                return 'D'
            elif score >= 45 and score < 50:
                return 'E'
            elif score >= 35 and score < 45:
                return 'F'
            else:
                return 'Ungraded'

        # Function to calculate GPA from progressive_test_1_score
        def get_gpa_from_progressive_score(score):
            if score >= 95 and score <= 100:
                return 4.00
            elif score >= 80 and score < 95:
                return 3.67
            elif score >= 75 and score < 80:
                return 3.33
            elif score >= 70 and score < 75:
                return 3.00
            elif score >= 65 and score < 70:
                return 2.67
            elif score >= 60 and score < 65:
                return 2.33
            elif score >= 50 and score < 60:
                return 2.00
            elif score >= 45 and score < 50:
                return 1.67
            elif score >= 35 and score < 45:
                return 1.00
            else:
                return 0.00

        # Loop over the scores to populate students_data
        for score in scores:
            student_id = score.student.id

            if student_id not in students_data:
                students_data[student_id] = {
                    'student_name': score.student.fullname,
                    'student_id': score.student.id,
                    'class_year': score.student.class_year.name,  # Assuming class_year is a related field
                    'scores': [],
                    'total_score': 0,
                    'final_gpa': 0,
                }

            # Only consider the progressive_test_1_score
            progressive_test_1_score = score.progressive_test_1_score

            # Assign grade and GPA based on progressive_test_1_score
            grade = get_grade_from_progressive_score(progressive_test_1_score)
            score_gpa = get_gpa_from_progressive_score(progressive_test_1_score)

            # Add the score details for each student and subject
            students_data[student_id]['scores'].append({
                'subject_name': score.subject.name,
                'progressive_test_1_score': progressive_test_1_score,
                'grade': grade,
                'score_gpa': score_gpa,
                'score_id': score.id
            })

            # Accumulate the total score and GPA for the student
            students_data[student_id]['total_score'] += progressive_test_1_score
            students_data[student_id]['final_gpa'] += score_gpa

        # After populating data, calculate final grade and final GPA
        for student_id, data in students_data.items():
            total_score = data['total_score']
            data['final_grade'] = get_grade_from_progressive_score(total_score)
            data['final_gpa'] = data['final_gpa']  # Final GPA is accumulated GPA across all subjects

        # Include term in the JSON response
        students_list = list(students_data.values())

        return JsonResponse({
            'students': students_list,
            'term': term.term_name,
            "term_id": term.id,
        })

    except Term.DoesNotExist:
        return JsonResponse({'error': 'Invalid term provided'}, status=404)



# Viewing Saved Progressive Test Two Scores by Term:
@login_required(login_url='login')
def view_progressive_two_test_scores(request, term_id=None):
    # Ensure that term_id is provided
    if not term_id:
        return JsonResponse({'error': 'Term is required'}, status=400)

    try:
        # Fetch the term object
        term = Term.objects.get(id=term_id)

        # Fetch all scores for the selected term and the students that belong to it
        scores = Score.objects.filter(term=term)

        # Prepare a dictionary to store the student data
        students_data = {}

        # Function to calculate grade from progressive_test_2_score
        def get_grade_from_progressive_score(score):
            if score >= 95 and score <= 100:
                return 'A*'
            elif score >= 80 and score < 95:
                return 'A'
            elif score >= 75 and score < 80:
                return 'B+'
            elif score >= 70 and score < 75:
                return 'B'
            elif score >= 65 and score < 70:
                return 'C+'
            elif score >= 60 and score < 65:
                return 'C'
            elif score >= 50 and score < 60:
                return 'D'
            elif score >= 45 and score < 50:
                return 'E'
            elif score >= 35 and score < 45:
                return 'F'
            else:
                return 'Ungraded'

        # Function to calculate GPA from progressive_test_2_score
        def get_gpa_from_progressive_score(score):
            if score >= 95 and score <= 100:
                return 4.00
            elif score >= 80 and score < 95:
                return 3.67
            elif score >= 75 and score < 80:
                return 3.33
            elif score >= 70 and score < 75:
                return 3.00
            elif score >= 65 and score < 70:
                return 2.67
            elif score >= 60 and score < 65:
                return 2.33
            elif score >= 50 and score < 60:
                return 2.00
            elif score >= 45 and score < 50:
                return 1.67
            elif score >= 35 and score < 45:
                return 1.00
            else:
                return 0.00

        # Loop over the scores to populate students_data
        for score in scores:
            student_id = score.student.id

            if student_id not in students_data:
                students_data[student_id] = {
                    'student_name': score.student.fullname,
                    'student_id': score.student.id,
                    'class_year': score.student.class_year.name,  # Assuming class_year is a related field
                    'scores': [],
                    'total_score': 0,
                    'final_gpa': 0,
                }

            # Only consider the progressive_test_2_score
            progressive_test_2_score = score.progressive_test_2_score

            # Assign grade and GPA based on progressive_test_2_score
            grade = get_grade_from_progressive_score(progressive_test_2_score)
            score_gpa = get_gpa_from_progressive_score(progressive_test_2_score)

            # Add the score details for each student and subject
            students_data[student_id]['scores'].append({
                'subject_name': score.subject.name,
                'progressive_test_2_score': progressive_test_2_score,
                'grade': grade,
                'score_gpa': score_gpa,
                'score_id': score.id
            })

            # Accumulate the total score and GPA for the student
            students_data[student_id]['total_score'] += progressive_test_2_score
            students_data[student_id]['final_gpa'] += score_gpa

        # After populating data, calculate final grade and final GPA
        for student_id, data in students_data.items():
            total_score = data['total_score']
            data['final_grade'] = get_grade_from_progressive_score(total_score)
            data['final_gpa'] = data['final_gpa']  # Final GPA is accumulated GPA across all subjects

        # Include term in the JSON response
        students_list = list(students_data.values())

        return JsonResponse({
            'students': students_list,
            'term': term.term_name,
            "term_id": term.id,
        })

    except Term.DoesNotExist:
        return JsonResponse({'error': 'Invalid term provided'}, status=404)



# Viewing Saved Progressive Test Three Scores by Term:
@login_required(login_url='login')
def view_progressive_three_test_scores(request, term_id=None):
    # Ensure that term_id is provided
    if not term_id:
        return JsonResponse({'error': 'Term is required'}, status=400)

    try:
        # Fetch the term object
        term = Term.objects.get(id=term_id)

        # Fetch all scores for the selected term and the students that belong to it
        scores = Score.objects.filter(term=term)

        # Prepare a dictionary to store the student data
        students_data = {}

        # Function to calculate grade from progressive_test_3_score
        def get_grade_from_progressive_score(score):
            if score >= 95 and score <= 100:
                return 'A*'
            elif score >= 80 and score < 95:
                return 'A'
            elif score >= 75 and score < 80:
                return 'B+'
            elif score >= 70 and score < 75:
                return 'B'
            elif score >= 65 and score < 70:
                return 'C+'
            elif score >= 60 and score < 65:
                return 'C'
            elif score >= 50 and score < 60:
                return 'D'
            elif score >= 45 and score < 50:
                return 'E'
            elif score >= 35 and score < 45:
                return 'F'
            else:
                return 'Ungraded'

        # Function to calculate GPA from progressive_test_3_score
        def get_gpa_from_progressive_score(score):
            if score >= 95 and score <= 100:
                return 4.00
            elif score >= 80 and score < 95:
                return 3.67
            elif score >= 75 and score < 80:
                return 3.33
            elif score >= 70 and score < 75:
                return 3.00
            elif score >= 65 and score < 70:
                return 2.67
            elif score >= 60 and score < 65:
                return 2.33
            elif score >= 50 and score < 60:
                return 2.00
            elif score >= 45 and score < 50:
                return 1.67
            elif score >= 35 and score < 45:
                return 1.00
            else:
                return 0.00

        # Loop over the scores to populate students_data
        for score in scores:
            student_id = score.student.id

            if student_id not in students_data:
                students_data[student_id] = {
                    'student_name': score.student.fullname,
                    'student_id': score.student.id,
                    'class_year': score.student.class_year.name,  # Assuming class_year is a related field
                    'scores': [],
                    'total_score': 0,
                    'final_gpa': 0,
                }

            # Only consider the progressive_test_3_score
            progressive_test_3_score = score.progressive_test_3_score

            # Assign grade and GPA based on progressive_test_3_score
            grade = get_grade_from_progressive_score(progressive_test_3_score)
            score_gpa = get_gpa_from_progressive_score(progressive_test_3_score)

            # Add the score details for each student and subject
            students_data[student_id]['scores'].append({
                'subject_name': score.subject.name,
                'progressive_test_3_score': progressive_test_3_score,
                'grade': grade,
                'score_gpa': score_gpa,
                'score_id': score.id
            })

            # Accumulate the total score and GPA for the student
            students_data[student_id]['total_score'] += progressive_test_3_score
            students_data[student_id]['final_gpa'] += score_gpa

        # After populating data, calculate final grade and final GPA
        for student_id, data in students_data.items():
            total_score = data['total_score']
            data['final_grade'] = get_grade_from_progressive_score(total_score)
            data['final_gpa'] = data['final_gpa']  # Final GPA is accumulated GPA across all subjects

        # Include term in the JSON response
        students_list = list(students_data.values())

        return JsonResponse({
            'students': students_list,
            'term': term.term_name,
            "term_id": term.id,
        })

    except Term.DoesNotExist:
        return JsonResponse({'error': 'Invalid term provided'}, status=404)
