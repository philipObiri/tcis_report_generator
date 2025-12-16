from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from .models import (
    Level, ClassYear, 
    Term, Subject, Student, TeacherProfile,
    Score, AcademicReport,MidtermReport,
    ProgressiveTestOneReport,ProgressiveTestTwoReport,
    MockReport,
)
from django.shortcuts import render
from django.template.loader import render_to_string
from decimal import Decimal 
from django.shortcuts import get_object_or_404
from reports.utils import calculate_gpa
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


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
    is_head_class_teacher = False
    try :
        teacher_profile = TeacherProfile.objects.get(user=request.user)
        is_head_class_teacher = teacher_profile.is_head_class_teacher
    except TeacherProfile.DoesNotExist:
        pass


    students = []
    scores = []
    term = None
    subject = None
    class_year = None

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Retrieve POST parameters for filters
        level_id = request.POST.get('level')
        class_year_id = request.POST.get('class_year')
        term_id = request.POST.get('term')
        subject_id = request.POST.get('subject')

        try:
            level = Level.objects.get(id=level_id) if level_id else None
            class_year = ClassYear.objects.get(id=class_year_id) if class_year_id else None
            term = Term.objects.get(id=term_id) if term_id else None
            subject = Subject.objects.get(id=subject_id) if subject_id else None

            if not all([class_year, term, subject]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please select class year, term, and subject.'
                })

            students = Student.objects.filter(class_year=class_year)

            # Process the submitted classwork scores
            for student in students:
                posted_class_score = request.POST.get(f'class_score_{student.id}')
                if posted_class_score and posted_class_score.strip():
                    try:
                        class_work_score = Decimal(posted_class_score.strip())

                        score_instance, created = Score.objects.update_or_create(
                            student=student,
                            term=term,
                            subject=subject,
                            created_by=request.user,
                            defaults={'class_work_score': class_work_score}
                        )

                        # The save method is automatically called by update_or_create
                        # But we can explicitly call it to ensure calculations are updated
                        score_instance.save()

                    except (ValueError, TypeError) as e:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Invalid score value for {student.fullname}: {posted_class_score}'
                        })

            return JsonResponse({
                'status': 'success',
                'message': 'Classwork scores saved successfully!'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            })

    # Handle GET request for retrieving scores
    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')
    class_year_id = request.GET.get('class_year')
    
    if term_id and subject_id:
        try:
            term = Term.objects.get(id=term_id)
            subject = Subject.objects.get(id=subject_id)
            
            # Filter scores based on available parameters
            score_filter = {
                'term': term,
                'subject': subject,
                'created_by': request.user
            }
            
            if class_year_id:
                class_year = ClassYear.objects.get(id=class_year_id)
                students = Student.objects.filter(class_year=class_year)
                score_filter['student__class_year'] = class_year
            else:
                students = Student.objects.all()
            
            scores = Score.objects.filter(**score_filter).select_related('student', 'subject', 'term')
            
        except (Term.DoesNotExist, Subject.DoesNotExist, ClassYear.DoesNotExist):
            pass
    else:
        students = Student.objects.all()

    return render(request, 'class_scores.html', {
        'students': students,
        'scores': scores,
        'term': term,
        'subject': subject,
        'class_year': class_year,
        'is_head_class_teacher': is_head_class_teacher,
    })


#=========== Process First Progressive Test Scores =====================
@login_required(login_url='login')
def progressive_test_scores_one(request):
    is_head_class_teacher = False
    try :
        teacher_profile = TeacherProfile.objects.get(user=request.user)
        is_head_class_teacher = teacher_profile.is_head_class_teacher
    except TeacherProfile.DoesNotExist:
        pass


    students = []
    scores = []
    term = None
    subject = None
    class_year = None

    if request.method == 'POST':
        level_id = request.POST.get('level')
        class_year_id = request.POST.get('class_year')
        term_id = request.POST.get('term')
        subject_id = request.POST.get('subject')

        try:
            if not all([class_year_id, term_id, subject_id]):
                messages.error(request, 'Please select class year, term, and subject.')
                return redirect('progressive_score_one')

            class_year = ClassYear.objects.get(id=class_year_id)
            term = Term.objects.get(id=term_id)
            subject = Subject.objects.get(id=subject_id)
            students = Student.objects.filter(class_year=class_year)

            for student in students:
                progressive_test_1_score = request.POST.get(f'progressive_test_1_score_{student.id}')
                if progressive_test_1_score and progressive_test_1_score.strip():
                    try:
                        score_value = Decimal(progressive_test_1_score.strip())

                        score_instance, created = Score.objects.update_or_create(
                            student=student,
                            term=term,
                            subject=subject,
                            created_by=request.user,
                            defaults={'progressive_test_1_score': score_value}
                        )

                        # Ensure recalculation after saving the score
                        score_instance.save()

                    except (ValueError, TypeError):
                        messages.error(request, f'Invalid score value for {student.fullname}: {progressive_test_1_score}')
                        return redirect('progressive_score_one')

            messages.success(request, 'Progressive test 1 data saved successfully.')
            # Redirect with parameters to maintain context
            return redirect(f'progressive_score_one?term={term_id}&subject={subject_id}&class_year={class_year_id}')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('progressive_score_one')

    # Handle GET request
    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')
    class_year_id = request.GET.get('class_year')

    if term_id and subject_id:
        try:
            term = Term.objects.get(id=term_id)
            subject = Subject.objects.get(id=subject_id)
            
            score_filter = {
                'term': term,
                'subject': subject,
                'created_by': request.user
            }
            
            if class_year_id:
                class_year = ClassYear.objects.get(id=class_year_id)
                students = Student.objects.filter(class_year=class_year)
                score_filter['student__class_year'] = class_year
            else:
                students = Student.objects.all()
            
            scores = Score.objects.filter(**score_filter).select_related('student', 'subject', 'term')
            
        except (Term.DoesNotExist, Subject.DoesNotExist, ClassYear.DoesNotExist):
            students = Student.objects.all()
    else:
        students = Student.objects.all()

    context = {
        'students': students,
        'scores': scores,
        'term': term,
        'subject': subject,
        'class_year': class_year,
        'is_head_class_teacher': is_head_class_teacher,
    }

    return render(request, 'progressive_tests/progressive_test_1.html', context)





#=========== Process Second Progressive Test Scores =====================
@login_required(login_url='login')
def progressive_test_scores_two(request):
    is_head_class_teacher = False
    try :
        teacher_profile = TeacherProfile.objects.get(user=request.user)
        is_head_class_teacher = teacher_profile.is_head_class_teacher
    except TeacherProfile.DoesNotExist:
        pass


    students = []
    scores = []
    term = None
    subject = None
    class_year = None

    if request.method == 'POST':
        level_id = request.POST.get('level')
        class_year_id = request.POST.get('class_year')
        term_id = request.POST.get('term')
        subject_id = request.POST.get('subject')

        try:
            if not all([class_year_id, term_id, subject_id]):
                messages.error(request, 'Please select class year, term, and subject.')
                return redirect('progressive_score_two')

            class_year = ClassYear.objects.get(id=class_year_id)
            term = Term.objects.get(id=term_id)
            subject = Subject.objects.get(id=subject_id)
            students = Student.objects.filter(class_year=class_year)

            for student in students:
                progressive_test_2_score = request.POST.get(f'progressive_test_2_score_{student.id}')
                if progressive_test_2_score and progressive_test_2_score.strip():
                    try:
                        score_value = Decimal(progressive_test_2_score.strip())

                        score_instance, created = Score.objects.update_or_create(
                            student=student,
                            term=term,
                            subject=subject,
                            created_by=request.user,
                            defaults={'progressive_test_2_score': score_value}
                        )

                        score_instance.save()

                    except (ValueError, TypeError):
                        messages.error(request, f'Invalid score value for {student.fullname}: {progressive_test_2_score}')
                        return redirect('progressive_score_two')

            messages.success(request, 'Progressive Test 2 data saved successfully.')
            return redirect(f'progressive_score_two?term={term_id}&subject={subject_id}&class_year={class_year_id}')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('progressive_score_two')

    # Handle GET request
    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')
    class_year_id = request.GET.get('class_year')

    if term_id and subject_id:
        try:
            term = Term.objects.get(id=term_id)
            subject = Subject.objects.get(id=subject_id)
            
            score_filter = {
                'term': term,
                'subject': subject,
                'created_by': request.user
            }
            
            if class_year_id:
                class_year = ClassYear.objects.get(id=class_year_id)
                students = Student.objects.filter(class_year=class_year)
                score_filter['student__class_year'] = class_year
            else:
                students = Student.objects.all()
            
            scores = Score.objects.filter(**score_filter).select_related('student', 'subject', 'term')
            
        except (Term.DoesNotExist, Subject.DoesNotExist, ClassYear.DoesNotExist):
            students = Student.objects.all()
    else:
        students = Student.objects.all()

    context = {
        'students': students,
        'scores': scores,
        'term': term,
        'subject': subject,
        'class_year': class_year,
        'is_head_class_teacher': is_head_class_teacher,
    }

    return render(request, 'progressive_tests/progressive_test_2.html', context)



#=========== Process Third Progressive Test Scores =====================
@login_required(login_url='login')
def progressive_test_scores_three(request):

    is_head_class_teacher = False
    try :
        teacher_profile = TeacherProfile.objects.get(user=request.user)
        is_head_class_teacher = teacher_profile.is_head_class_teacher
    except TeacherProfile.DoesNotExist:
        pass

    students = []
    scores = []
    term = None
    subject = None
    class_year = None

    if request.method == 'POST':
        level_id = request.POST.get('level')
        class_year_id = request.POST.get('class_year')
        term_id = request.POST.get('term')
        subject_id = request.POST.get('subject')

        try:
            if not all([class_year_id, term_id, subject_id]):
                messages.error(request, 'Please select class year, term, and subject.')
                return redirect('progressive_score_three')

            class_year = ClassYear.objects.get(id=class_year_id)
            term = Term.objects.get(id=term_id)
            subject = Subject.objects.get(id=subject_id)
            students = Student.objects.filter(class_year=class_year)

            for student in students:
                progressive_test_3_score = request.POST.get(f'progressive_test_3_score_{student.id}')
                if progressive_test_3_score and progressive_test_3_score.strip():
                    try:
                        score_value = Decimal(progressive_test_3_score.strip())

                        score_instance, created = Score.objects.update_or_create(
                            student=student,
                            term=term,
                            subject=subject,
                            created_by=request.user,
                            defaults={'progressive_test_3_score': score_value}
                        )

                        score_instance.save()

                    except (ValueError, TypeError):
                        messages.error(request, f'Invalid score value for {student.fullname}: {progressive_test_3_score}')
                        return redirect('progressive_score_three')

            messages.success(request, 'Progressive Test 3 data saved successfully.')
            return redirect(f'progressive_score_three?term={term_id}&subject={subject_id}&class_year={class_year_id}')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('progressive_score_three')

    # Handle GET request
    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')
    class_year_id = request.GET.get('class_year')

    if term_id and subject_id:
        try:
            term = Term.objects.get(id=term_id)
            subject = Subject.objects.get(id=subject_id)
            
            score_filter = {
                'term': term,
                'subject': subject,
                'created_by': request.user
            }
            
            if class_year_id:
                class_year = ClassYear.objects.get(id=class_year_id)
                students = Student.objects.filter(class_year=class_year)
                score_filter['student__class_year'] = class_year
            else:
                students = Student.objects.all()
            
            scores = Score.objects.filter(**score_filter).select_related('student', 'subject', 'term')
            
        except (Term.DoesNotExist, Subject.DoesNotExist, ClassYear.DoesNotExist):
            students = Student.objects.all()
    else:
        students = Student.objects.all()

    context = {
        'students': students,
        'scores': scores,
        'term': term,
        'subject': subject,
        'class_year': class_year,
        'is_head_class_teacher': is_head_class_teacher,
    }

    return render(request, 'progressive_tests/progressive_test_3.html', context)



#========== Process MidTerm Scores ====================
@login_required(login_url='login')
def midterm_scores(request):
    is_head_class_teacher = False
    try :
        teacher_profile = TeacherProfile.objects.get(user=request.user)
        is_head_class_teacher = teacher_profile.is_head_class_teacher
    except TeacherProfile.DoesNotExist:
        pass

    students = []
    scores = []
    term = None
    subject = None
    class_year = None

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Retrieve POST parameters for filters
        level_id = request.POST.get('level')
        class_year_id = request.POST.get('class_year')
        term_id = request.POST.get('term')
        subject_id = request.POST.get('subject')

        try:
            level = Level.objects.get(id=level_id) if level_id else None
            class_year = ClassYear.objects.get(id=class_year_id) if class_year_id else None
            term = Term.objects.get(id=term_id) if term_id else None
            subject = Subject.objects.get(id=subject_id) if subject_id else None

            if not all([class_year, term, subject]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please select class year, term, and subject.'
                })

            students = Student.objects.filter(class_year=class_year)

            for student in students:
                posted_midterm_score = request.POST.get(f'midterm_score_{student.id}')
                if posted_midterm_score and posted_midterm_score.strip():
                    try:
                        midterm_score = Decimal(posted_midterm_score.strip())

                        # Update or create the score instance and save
                        score_instance, created = Score.objects.update_or_create(
                            student=student,
                            term=term,
                            subject=subject,
                            created_by=request.user,
                            defaults={'midterm_score': midterm_score}
                        )

                        # Explicit save to ensure calculations are updated
                        score_instance.save()

                    except (ValueError, TypeError):
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Invalid midterm score value for {student.fullname}: {posted_midterm_score}'
                        })

            return JsonResponse({
                'status': 'success',
                'message': 'Midterm scores saved successfully!'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            })

    # Handle GET request
    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')
    class_year_id = request.GET.get('class_year')

    if term_id and subject_id:
        try:
            term = Term.objects.get(id=term_id)
            subject = Subject.objects.get(id=subject_id)
            
            score_filter = {
                'term': term,
                'subject': subject,
                'created_by': request.user
            }
            
            if class_year_id:
                class_year = ClassYear.objects.get(id=class_year_id)
                students = Student.objects.filter(class_year=class_year)
                score_filter['student__class_year'] = class_year
            else:
                students = Student.objects.all()
            
            scores = Score.objects.filter(**score_filter).select_related('student', 'subject', 'term')
            
        except (Term.DoesNotExist, Subject.DoesNotExist, ClassYear.DoesNotExist):
            students = Student.objects.all()
    else:
        students = Student.objects.all()

    context = {
        'students': students,
        'scores': scores,
        'term': term,
        'subject': subject,
        'class_year': class_year,
        'is_head_class_teacher': is_head_class_teacher,
    }

    return render(request, 'midterm.html', context)


#========== Process Mock Scores ====================
@login_required(login_url='login')
def mock_scores(request):

    is_head_class_teacher = False
    try :
        teacher_profile = TeacherProfile.objects.get(user=request.user)
        is_head_class_teacher = teacher_profile.is_head_class_teacher
    except TeacherProfile.DoesNotExist:
        pass


    students = []
    scores = []
    term = None
    subject = None
    class_year = None

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Retrieve POST parameters for filters
        level_id = request.POST.get('level')
        class_year_id = request.POST.get('class_year')
        term_id = request.POST.get('term')
        subject_id = request.POST.get('subject')

        try:
            level = Level.objects.get(id=level_id) if level_id else None
            class_year = ClassYear.objects.get(id=class_year_id) if class_year_id else None
            term = Term.objects.get(id=term_id) if term_id else None
            subject = Subject.objects.get(id=subject_id) if subject_id else None

            if not all([class_year, term, subject]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please select class year, term, and subject.'
                })

            students = Student.objects.filter(class_year=class_year)

            for student in students:
                posted_mock_score = request.POST.get(f'mock_score_{student.id}')
                if posted_mock_score and posted_mock_score.strip():
                    try:
                        mock_score = Decimal(posted_mock_score.strip())

                        # Update or create the score instance and save
                        score_instance, created = Score.objects.update_or_create(
                            student=student,
                            term=term,
                            subject=subject,
                            created_by=request.user,
                            defaults={'mock_score': mock_score}
                        )

                        # Explicit save to ensure calculations are updated
                        score_instance.save()

                    except (ValueError, TypeError):
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Invalid mock score value for {student.fullname}: {posted_mock_score}'
                        })

            return JsonResponse({
                'status': 'success',
                'message': 'Mock Scores saved successfully!'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            })

    # Handle GET request
    term_id = request.GET.get('term')
    subject_id = request.GET.get('subject')
    class_year_id = request.GET.get('class_year')

    if term_id and subject_id:
        try:
            term = Term.objects.get(id=term_id)
            subject = Subject.objects.get(id=subject_id)
            
            score_filter = {
                'term': term,
                'subject': subject,
                'created_by': request.user
            }
            
            if class_year_id:
                class_year = ClassYear.objects.get(id=class_year_id)
                students = Student.objects.filter(class_year=class_year)
                score_filter['student__class_year'] = class_year
            else:
                students = Student.objects.all()
            
            scores = Score.objects.filter(**score_filter).select_related('student', 'subject', 'term')
            
        except (Term.DoesNotExist, Subject.DoesNotExist, ClassYear.DoesNotExist):
            students = Student.objects.all()
    else:
        students = Student.objects.all()

    context = {
        'students': students,
        'scores': scores,
        'term': term,
        'subject': subject,
        'class_year': class_year,
        'is_head_class_teacher': is_head_class_teacher,
    }

    return render(request, 'mock_scores.html', context)



##=============== Logic for processing and display the saved end of term scores for the user ===============
@login_required(login_url='login')
def process_scores_view(request):
    is_head_class_teacher = False
    try :
        teacher_profile = TeacherProfile.objects.get(user=request.user)
        is_head_class_teacher = teacher_profile.is_head_class_teacher
    except TeacherProfile.DoesNotExist:
        pass

    formset = None
    students = []
    scores = []

    # Fetch all students and their scores (including continuous_assessment) for the logged-in user
    students = Student.objects.all()  # Adjust as per your filter
    scores = Score.objects.filter(created_by=request.user)  # Fetch scores entered by the logged-in user
    # scores = Score.objects.all()

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

            # Fetch comments from POST request (only for head class teachers)
            academic_comment = request.POST.get(f'academic_comment_{student.id}', '').strip()
            behavioral_comment = request.POST.get(f'behavioral_comment_{student.id}', '').strip()

            try:
                # Convert exam_score to Decimal, if it's not 0.0
                exam_score = Decimal(str(exam_score)) if exam_score else Decimal('0.0')
            except:
                exam_score = Decimal('0.0')  # If the value can't be converted, set to 0.0

            # If a score exists for the student, use that to fetch or update the score
            if existing_score:
                # Update existing score (don't manually recalculate)
                existing_score.exam_score = exam_score

                # Update comments (only if user is head class teacher)
                if is_head_class_teacher:
                    existing_score.academic_comment = academic_comment if academic_comment else existing_score.academic_comment
                    existing_score.behavioral_comment = behavioral_comment if behavioral_comment else existing_score.behavioral_comment

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

                # Add comments if user is head class teacher
                if is_head_class_teacher:
                    new_score.academic_comment = academic_comment
                    new_score.behavioral_comment = behavioral_comment

                new_score.save()  # This will trigger the `save()` method to calculate total_score and grade

        return JsonResponse({'status': 'success', 'message': 'End of Term Scores saved successfully!'})

    return render(request, 'dashboard.html', {
        'formset': formset,
        'students': students,
        'scores': scores,
        'is_head_class_teacher': is_head_class_teacher,
    })




# Functional Logic to fetch all end of term scores :
# @login_required(login_url='login')
# def view_academic_report(request, student_id, term_id):
#     try:
#         student = Student.objects.get(id=student_id)
#         scores = Score.objects.filter(student=student, term=term_id, subject__in=student.subjects.all())
#         term = get_object_or_404(Term, id=term_id)
        
#         # Ensure that class_year is serialized to a string or relevant field
#         class_year = student.class_year.name if hasattr(student.class_year, 'name') else str(student.class_year)

#         # Calculate GPA based on scores (e.g., using weighted average of grades)
#         gpa = calculate_gpa(scores)

#         # Prepare data to be returned in the JSON response
#         report = {
#             'student_name': student.fullname,
#             'class_year': class_year,  # Ensure it's a serializable value (e.g., string)
#             'term': term.term_name,
#             'gpa': gpa,
#             'scores': [
#                 {
#                     'subject': score.subject.name,
#                     'ca': score.continuous_assessment,
#                     'exam': score.exam_score,
#                     'total': score.total_score,  # Assuming you have a method to calculate total score
#                     'grade': score.grade
#                 }
#                 for score in scores
#             ]
#         }

#         # Return a JsonResponse with the report data
#         return JsonResponse(report)

#     except Student.DoesNotExist:
#         return JsonResponse({'error': 'Student not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)



@login_required(login_url='login')
def view_academic_report(request, student_id, term_id):
    try:
        student = Student.objects.get(id=student_id)
        
        # ✅ Only get scores for subjects assigned to the student (latest score per subject)
        scores = Score.objects.filter(
            student=student,
            term=term_id,
            subject__in=student.subjects.all()
        ).order_by('subject', '-updated_at').distinct('subject')

        term = get_object_or_404(Term, id=term_id)
        class_year = student.class_year.name if hasattr(student.class_year, 'name') else str(student.class_year)

        gpa = calculate_gpa(scores)

        report = {
            'student_name': student.fullname,
            'class_year': class_year,
            'term': term.term_name,
            'gpa': round(float(gpa), 2),
            'scores': [
                {
                    'subject': score.subject.name,
                    'ca': round(float(score.continuous_assessment), 2),
                    'exam': round(float(score.exam_score) * 0.70, 2),  # Show 70% of exam score, rounded
                    'total': round(float(score.total_score), 2),
                    'grade': score.grade
                }
                for score in scores
            ]
        }

        return JsonResponse(report)

    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Functional Logic to fetch all midterm test scores :
@login_required(login_url='login')
def view_midterm_report(request, student_id, term_id):
    try:
        student = Student.objects.get(id=student_id)
        scores = Score.objects.filter(
            student=student,
            term=term_id,
            subject__in=student.subjects.all()
        ).order_by('subject', '-updated_at').distinct('subject').order_by('subject', '-updated_at').distinct('subject')
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



# Functional Logic to fetch all mock test scores :
@login_required(login_url='login')
def view_mock_report(request, student_id, term_id):
    try:
        student = Student.objects.get(id=student_id)
        scores = Score.objects.filter(
            student=student,
            term=term_id,
            subject__in=student.subjects.all()
        ).order_by('subject', '-updated_at').distinct('subject').order_by('subject', '-updated_at').distinct('subject')
        term = get_object_or_404(Term, id=term_id)
        
        # Ensure that class_year is serialized to a string or relevant field
        class_year = student.class_year.name if hasattr(student.class_year, 'name') else str(student.class_year)

        # Function to calculate grade based on progressive_test_1_score
        def get_grade_from_mock_score(score):
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
        def get_gpa_from_mock_score(score):
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
            total_score = sum([score.mock_score for score in scores])
            total_score_percentage = float(total_score) / (len(scores) * 100) * 100  # Cast to float
        else:
            total_score_percentage = 0.0  # If no scores exist, default to 0%

        # Calculate GPA based on total score percentage
        total_gpa = get_gpa_from_mock_score(total_score_percentage)

        # Prepare data to be returned in the JSON response
        mock_report = {
            'student_name': student.fullname,
            'class_year': class_year,  # Ensure it's a serializable value (e.g., string)
            'term': term.term_name,
            'total_score_percentage': total_score_percentage,
            'total_gpa': total_gpa,  # Add the total GPA
            'scores': [
                {
                    'subject': score.subject.name,
                    'mock_score': score.mock_score,
                    'grade': get_grade_from_mock_score(score.mock_score),  # Grade based on progressive test score
                    'gpa': get_gpa_from_mock_score(score.mock_score)  # GPA based on individual score
                }
                for score in scores
            ]
        }

        # Return a JsonResponse with the midterm report data
        return JsonResponse(mock_report)

    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




# # Functional Logic to fetch all progressive test one scores :
@login_required(login_url='login')
def view_progressive_test_score_one_report(request, student_id, term_id):
    try:
        student = Student.objects.get(id=student_id)
        scores = Score.objects.filter(
            student=student,
            term=term_id,
            subject__in=student.subjects.all()
        ).order_by('subject', '-updated_at').distinct('subject')
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
        scores = Score.objects.filter(
            student=student,
            term=term_id,
            subject__in=student.subjects.all()
        ).order_by('subject', '-updated_at').distinct('subject')
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
        scores = Score.objects.filter(
            student=student,
            term=term_id,
            subject__in=student.subjects.all()
        ).order_by('subject', '-updated_at').distinct('subject')
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
@login_required(login_url='login')
def get_levels(request):
    levels = Level.objects.all()

    # Serialize the levels into a list of dictionaries
    levels_data = [{'id': level.id, 'name': level.name} for level in levels]

    return JsonResponse({"levels": levels_data})


# Fetch classes based on selected level
@login_required(login_url='login')
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
@login_required(login_url='login')
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
@login_required(login_url='login')
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




## Fetch students based on selected filters
@login_required(login_url='login')
def get_students_by_filters(request, level_id, class_year_id, term_id, subject_id):
    try:
        # Get the selected objects based on the filters
        level = Level.objects.get(id=level_id)
        class_year = ClassYear.objects.get(id=class_year_id)
        term = Term.objects.get(id=term_id)
        subject = Subject.objects.get(id=subject_id)

        # Fetch students based on the selected class year and subject, ordered alphabetically
        students = Student.objects.filter(class_year=class_year, subjects=subject).order_by('fullname')

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
                    'mock_score': str(score.mock_score),
                    'exam_score': str(score.exam_score),
                    'continuous_assessment': str(score.continuous_assessment),
                    'total_score': str(score.total_score),
                    'grade': score.grade,
                    'academic_comment': score.academic_comment or '',
                    'behavioral_comment': score.behavioral_comment or ''
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



# @require_POST
# def get_comment(request):
#     try:
#         data = json.loads(request.body)
#         student_name = data.get('student_name')
#         class_year = data.get('class_year')
#         term_name = data.get('term')

#         student = Student.objects.get(fullname=student_name)
#         class_year_obj = ClassYear.objects.get(name=class_year)
#         term = Term.objects.get(term_name=term_name, class_year=class_year_obj)

#         report = AcademicReport.objects.filter(student=student, term=term).first()
#         return JsonResponse({
#             'academic_comment': report.academic_comment if report else '',
#             'behavioral_comment': report.behavioral_comment if report else '',
#             'promotion': report.promotion if report else ''
#         })

#     except Exception:
#         return JsonResponse({
#             'academic_comment': '',
#             'behavioral_comment': '',
#             'promotion': ''
#         })


# @login_required(login_url='login')
# def generate_report(request):
#     is_head_class_teacher = False
#     try:
#         teacher_profile = TeacherProfile.objects.get(user=request.user)
#         is_head_class_teacher = teacher_profile.is_head_class_teacher
#     except TeacherProfile.DoesNotExist:
#         pass

#     if request.method == 'POST':
#         data = json.loads(request.body)
#         student_name = data.get('student_name')
#         class_year = data.get('class_year')
#         term_name = data.get('term')
#         academic_comment = data.get('academic_comment', '').strip()
#         behavioral_comment = data.get('behavioral_comment', '').strip()
#         promotion = data.get('promotion', '').strip()

#         if not academic_comment and not behavioral_comment:
#             return JsonResponse({'success': False, 'error': 'At least one comment is required before generating the report.'})

#         try:
#             student = Student.objects.get(fullname=student_name)
#             class_year_obj = ClassYear.objects.get(name=class_year)
#             term = Term.objects.get(term_name=term_name, class_year=class_year_obj)

#             scores = Score.objects.filter(student=student, term=term).distinct('subject')

#             if not scores.exists():
#                 return JsonResponse({
#                     'success': False,
#                     'error': f'No scores found for {student_name} in {term_name}.'
#                 })

#             academic_report, created = AcademicReport.objects.get_or_create(student=student, term=term)

#             if created:
#                 academic_report.student_scores.set(scores)

#             academic_report.academic_comment = academic_comment
#             academic_report.behavioral_comment = behavioral_comment
#             academic_report.promotion = promotion if promotion else None
#             academic_report.generated_by = request.user
#             academic_report.save()

#             print(f"Generated report for {student_name} in {term_name} with comments: {academic_comment}, {behavioral_comment}, Promotion: {promotion}")

#             report_html = render_to_string('generated_report.html', {
#                 'student_name': student_name,
#                 'class_year': class_year,
#                 'term_name': term_name,
#                 'gpa': academic_report.student_gpa,
#                 'report_data': scores,
#                 'is_head_class_teacher': is_head_class_teacher,
#                 'promotion': academic_report.promotion,
#                 'academic_comment': academic_comment,
#                 'behavioral_comment': behavioral_comment
#             })

#             return JsonResponse({'success': True, 'report_html': report_html})

#         except Student.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Student not found.'})
#         except Term.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Term not found.'})
#         except ClassYear.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Class Year not found.'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})



@require_POST
def get_comment(request):
    try:
        data = json.loads(request.body)
        student_name = data.get('student_name')
        class_year = data.get('class_year')
        term_name = data.get('term')

        # Validate required fields
        if not all([student_name, class_year, term_name]):
            return JsonResponse({
                'academic_comment': '',
                'behavioral_comment': '',
                'promotion': ''
            })

        student = Student.objects.get(fullname=student_name)
        class_year_obj = ClassYear.objects.get(name=class_year)
        term = Term.objects.get(term_name=term_name, class_year=class_year_obj)

        report = AcademicReport.objects.filter(student=student, term=term).first()
        
        return JsonResponse({
            'academic_comment': report.academic_comment if report and report.academic_comment else '',
            'behavioral_comment': report.behavioral_comment if report and report.behavioral_comment else '',
            'promotion': report.promotion if report and report.promotion else ''
        })

    except (Student.DoesNotExist, ClassYear.DoesNotExist, Term.DoesNotExist) as e:
        print(f"Error in get_comment: {str(e)}")
        return JsonResponse({
            'academic_comment': '',
            'behavioral_comment': '',
            'promotion': ''
        })
    except Exception as e:
        print(f"Unexpected error in get_comment: {str(e)}")
        return JsonResponse({
            'academic_comment': '',
            'behavioral_comment': '',
            'promotion': ''
        })


from django.views.decorators.http import require_GET

@require_GET
def get_promotion_choices(request):
    return JsonResponse({
        'choices': [choice[0] for choice in AcademicReport.PROMOTION_CHOICES]
    })


# @login_required(login_url='login')
# @require_POST
# def generate_report(request):
#     is_head_class_teacher = False
#     try:
#         teacher_profile = TeacherProfile.objects.get(user=request.user)
#         is_head_class_teacher = teacher_profile.is_head_class_teacher
#     except TeacherProfile.DoesNotExist:
#         pass

#     try:
#         data = json.loads(request.body)
#         student_name = data.get('student_name', '').strip()
#         class_year = data.get('class_year', '').strip()
#         term_name = data.get('term', '').strip()
#         academic_comment = data.get('academic_comment', '').strip()
#         behavioral_comment = data.get('behavioral_comment', '').strip()
#         promotion = data.get('promotion', '').strip()

#         # Validate required fields
#         if not all([student_name, class_year, term_name]):
#             return JsonResponse({
#                 'success': False, 
#                 'error': 'Student name, class year, and term are required.'
#             })

#         # Validate that at least one comment is provided
#         if not academic_comment and not behavioral_comment:
#             return JsonResponse({
#                 'success': False, 
#                 'error': 'At least one comment (academic or behavioral) is required before generating the report.'
#             })

#         # Get the student, class year, and term objects
#         try:
#             student = Student.objects.get(fullname=student_name)
#         except Student.DoesNotExist:
#             return JsonResponse({'success': False, 'error': f'Student "{student_name}" not found.'})

#         try:
#             class_year_obj = ClassYear.objects.get(name=class_year)
#         except ClassYear.DoesNotExist:
#             return JsonResponse({'success': False, 'error': f'Class Year "{class_year}" not found.'})

#         try:
#             term = Term.objects.get(term_name=term_name, class_year=class_year_obj)
#         except Term.DoesNotExist:
#             return JsonResponse({'success': False, 'error': f'Term "{term_name}" not found for class "{class_year}".'})

#         # Get scores for the student in this term
#         scores = Score.objects.filter(student=student, term=term, subject__in=student.subjects.all()).distinct('subject')

#         if not scores.exists():
#             return JsonResponse({
#                 'success': False,
#                 'error': f'No scores found for {student_name} in {term_name}. Please ensure scores have been entered.'
#             })

#         # Get or create the academic report
#         academic_report, created = AcademicReport.objects.get_or_create(
#             student=student, 
#             term=term,
#             defaults={
#                 'generated_by': request.user
#             }
#         )

#         # If it's a new report, set the student scores
#         if created:
#             academic_report.student_scores.set(scores)

#         # Update the report fields
#         academic_report.academic_comment = academic_comment
#         academic_report.behavioral_comment = behavioral_comment
        
#         # Handle promotion - debug logs
#         print(f"Received promotion value: '{promotion}'")
#         print(f"Term name: '{term_name}'")
#         print(f"Is Term 3: {term_name == 'Term 3'}")
        
#         # Handle promotion - only for Term 3
#         if term_name == 'Term 3':
#             if promotion:  # If promotion is provided and not empty
#                 academic_report.promotion = promotion
#                 print(f"Setting promotion to: '{promotion}'")
#             else:
#                 # Keep existing promotion if no new one provided
#                 print(f"No promotion provided, keeping existing: '{academic_report.promotion}'")
#         else:
#             # Clear promotion for non-Term 3 terms
#             academic_report.promotion = None
#             print("Clearing promotion for non-Term 3")

#         academic_report.generated_by = request.user
#         academic_report.save()

#         print(f"Final promotion saved: '{academic_report.promotion}'")

#         print(f"Generated report for {student_name} in {term_name}")
#         print(f"Academic comment: {academic_comment}")
#         print(f"Behavioral comment: {behavioral_comment}")
#         print(f"Promotion: {promotion if promotion else 'None'}")

#         # Render the report HTML
#         context = {
#             'student_name': student_name,
#             'class_year': class_year,
#             'term_name': term_name,
#             'gpa': academic_report.student_gpa,
#             'report_data': scores,
#             'is_head_class_teacher': is_head_class_teacher,
#             'promotion': academic_report.promotion,  # This will be None if not set
#             'academic_comment': academic_comment,
#             'behavioral_comment': behavioral_comment
#         }

#         report_html = render_to_string('generated_report.html', context)

#         return JsonResponse({
#             'success': True, 
#             'report_html': report_html,
#             'message': f'Report generated successfully for {student_name} in {term_name}'
#         })

#     except json.JSONDecodeError:
#         return JsonResponse({'success': False, 'error': 'Invalid JSON data provided.'})
#     except Exception as e:
#         print(f"Unexpected error in generate_report: {str(e)}")
#         return JsonResponse({'success': False, 'error': f'An unexpected error occurred: {str(e)}'})



@login_required(login_url='login')
@require_POST
def generate_report(request):
    is_head_class_teacher = False
    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
        is_head_class_teacher = teacher_profile.is_head_class_teacher
    except TeacherProfile.DoesNotExist:
        pass

    try:
        data = json.loads(request.body)
        student_name = data.get('student_name', '').strip()
        class_year = data.get('class_year', '').strip()
        term_name = data.get('term', '').strip()
        academic_comment = data.get('academic_comment', '').strip()
        behavioral_comment = data.get('behavioral_comment', '').strip()
        promotion = data.get('promotion', '').strip()

        if not all([student_name, class_year, term_name]):
            return JsonResponse({
                'success': False,
                'error': 'Student name, class year, and term are required.'
            })

        # Check if user is a head class teacher (Class Advisor) before allowing comments
        if (academic_comment or behavioral_comment) and not is_head_class_teacher:
            return JsonResponse({
                'success': False,
                'error': 'Only Class Advisors (Head Class Teachers) are authorized to add Academic and Behavioural Comments.'
            })

        if not academic_comment and not behavioral_comment:
            return JsonResponse({
                'success': False,
                'error': 'At least one comment (academic or behavioral) is required before generating the report.'
            })

        try:
            student = Student.objects.get(fullname=student_name)
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'Student "{student_name}" not found.'})

        try:
            class_year_obj = ClassYear.objects.get(name=class_year)
        except ClassYear.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'Class Year "{class_year}" not found.'})

        try:
            term = Term.objects.get(term_name=term_name, class_year=class_year_obj)
        except Term.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'Term "{term_name}" not found for class "{class_year}".'})

        # ✅ Filter scores by subjects assigned to student (latest score per subject)
        scores = Score.objects.filter(
            student=student,
            term=term,
            subject__in=student.subjects.all()
        ).order_by('subject', '-updated_at').distinct('subject')

        if not scores.exists():
            return JsonResponse({
                'success': False,
                'error': f'No scores found for {student_name} in {term_name}. Please ensure scores have been entered.'
            })

        academic_report, created = AcademicReport.objects.get_or_create(
            student=student,
            term=term,
            defaults={'generated_by': request.user}
        )

        # Update comments
        academic_report.academic_comment = academic_comment
        academic_report.behavioral_comment = behavioral_comment

        # Handle promotion (only for Term 3)
        if term_name == 'Term 3':
            if promotion:
                academic_report.promotion = promotion
        else:
            academic_report.promotion = None

        academic_report.generated_by = request.user

        # Save the report - this will automatically:
        # 1. Recalculate GPA using latest scores
        # 2. Update student_scores with latest scores
        # (See AcademicReport.save() method in models.py)
        academic_report.save()

        # Calculate GPA from the SAME scores being displayed (match preview exactly)
        gpa = calculate_gpa(scores)

        # Prepare report data with calculated 70% exam scores
        report_data = []
        for score in scores:
            score.exam_score_display = round(float(score.exam_score) * 0.70, 2)
            report_data.append(score)

        context = {
            'student_name': student_name,
            'class_year': class_year,
            'term_name': term_name,
            'gpa': round(float(gpa), 2),  # Use live-calculated GPA, same as preview
            'report_data': report_data,
            'is_head_class_teacher': is_head_class_teacher,
            'promotion': academic_report.promotion,
            'academic_comment': academic_comment,
            'behavioral_comment': behavioral_comment
        }

        report_html = render_to_string('generated_report.html', context)

        return JsonResponse({
            'success': True,
            'report_html': report_html,
            'message': f'Report generated successfully for {student_name} in {term_name}'
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data provided.'})
    except Exception as e:
        print(f"Unexpected error in generate_report: {str(e)}")
        return JsonResponse({'success': False, 'error': f'An unexpected error occurred: {str(e)}'})



# This logic allows me to generate midterm reports dynamically
@login_required(login_url='login')
def generate_midterm_report(request):
    is_head_class_teacher = False
    try :
        teacher_profile = TeacherProfile.objects.get(user=request.user)
        is_head_class_teacher = teacher_profile.is_head_class_teacher
    except TeacherProfile.DoesNotExist:
        pass
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

            # Fetch all scores for the student in the selected term (only for subjects assigned to student)
            scores = Score.objects.filter(
                student=student,
                term=term,
                subject__in=student.subjects.all()
            ).order_by('subject', '-updated_at').distinct('subject')

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

            # Calculate the total GPA based on all subjects' GPA
            total_gpa = 0
            subject_count = 0
            for score in scores:
                subject_gpa = get_gpa_from_midterm_score(score.midterm_score)
                total_gpa += subject_gpa
                subject_count += 1

            # If there are any subjects, calculate the average GPA
            if subject_count > 0:
                average_gpa = total_gpa / subject_count
            else:
                average_gpa = 0  # Default to 0 GPA if no subjects exist

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
                midterm_report.midterm_gpa = float(average_gpa)
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
                'average_gpa': round(float(average_gpa), 2),  # Round to 2 decimals
                'scores': [
                    {
                        'subject': score.subject.name,
                        'midterm_score': round(float(score.midterm_score), 2),  # Round to 2 decimals
                        'grade': get_grade_from_midterm_score(score.midterm_score),
                        'gpa': round(get_gpa_from_midterm_score(score.midterm_score), 2)  # Round to 2 decimals
                    }
                    for score in scores
                ]
            }

            # Render the HTML for the report using the 'generated_report.html' template
            report_html = render_to_string('generated_midterm_report.html', {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,
                'term_name': term.term_name,
                'gpa': round(float(average_gpa), 2),  # Round to 2 decimals
                'is_head_class_teacher': is_head_class_teacher,
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



# This logic allows me to generate midterm reports dynamically
@login_required(login_url='login')
def generate_mock_report(request):
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

            # Fetch all scores for the student in the selected term (only for subjects assigned to student)
            scores = Score.objects.filter(
                student=student,
                term=term,
                subject__in=student.subjects.all()
            ).order_by('subject', '-updated_at').distinct('subject')

            # Function to calculate grade based on midterm_score
            def get_grade_from_mock_score(score):
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
            def get_gpa_from_mock_score(score):
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

            # Calculate the total GPA based on all subjects' GPA
            total_gpa = 0
            subject_count = 0
            for score in scores:
                subject_gpa = get_gpa_from_mock_score(score.mock_score)
                total_gpa += subject_gpa
                subject_count += 1

            # If there are any subjects, calculate the average GPA
            if subject_count > 0:
                average_gpa = total_gpa / subject_count
            else:
                average_gpa = 0  # Default to 0 GPA if no subjects exist

            # Create or update the MockReport instance for this student and term
            mock_report, created = MockReport.objects.get_or_create(
                student=student,
                term=term
            )

            # If it's a new report, set the fields and save
            if created:
                # Set the necessary fields for the new report
                mock_report.student = student
                mock_report.term = term
                mock_report.mock_gpa = float(average_gpa)
                mock_report.generated_by = request.user  # Automatically set generated_by to the current user

                # Save the report first to generate an ID
                mock_report.save()

                # Set the scores to the MidtermReport (many-to-many relationship)
                mock_report.student_scores.set(scores)  # Set the full Score instances to the report

                # Save again after assigning the many-to-many relationship
                mock_report.save()

            # Prepare data to be returned in the JSON response
            mock_report_data = {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,  # Ensure it's a serializable value (e.g., string)
                'term': term.term_name,
                'average_gpa': round(float(average_gpa), 2),  # Round to 2 decimals
                'scores': [
                    {
                        'subject': score.subject.name,
                        'mock_score': round(float(score.mock_score), 2),  # Round to 2 decimals
                        'grade': get_grade_from_mock_score(score.mock_score),
                        'gpa': round(get_gpa_from_mock_score(score.mock_score), 2)  # Round to 2 decimals
                    }
                    for score in scores
                ]
            }

            # Render the HTML for the report using the 'generated_mock_report.html' template
            report_html = render_to_string('generated_mock_report.html', {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,
                'term_name': term.term_name,
                'gpa': round(float(average_gpa), 2),  # Round to 2 decimals
                'report_data': mock_report_data['scores'],  # Pass the scores directly
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

            # Fetch all scores for the student in the selected term (only for subjects assigned to student)
            scores = Score.objects.filter(
                student=student,
                term=term,
                subject__in=student.subjects.all()
            ).order_by('subject', '-updated_at').distinct('subject')

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

            # Calculate individual GPA scores for each subject and then average them
            individual_gpas = []
            for score in scores:
                if score.progressive_test_1_score is not None:
                    individual_gpas.append(get_gpa_from_progressive_test_1_score(score.progressive_test_1_score))

            # Calculate average GPA if there are any scores
            if individual_gpas:
                total_gpa = sum(individual_gpas) / len(individual_gpas)
            else:
                total_gpa = 0.00  # If no scores exist, default to 0 GPA

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
                'total_gpa': round(float(total_gpa), 2),  # Round to 2 decimals
                'scores': [
                    {
                        'subject': score.subject.name,
                        'progressive_test_1_score': round(float(score.progressive_test_1_score), 2),  # Round to 2 decimals
                        'grade': get_grade_from_progressive_test_1_score(score.progressive_test_1_score),
                        'gpa': round(get_gpa_from_progressive_test_1_score(score.progressive_test_1_score), 2)  # Round to 2 decimals
                    }
                    for score in scores
                ]
            }

            # Render the HTML for the report using the 'generated_progressive_report.html' template
            report_html = render_to_string('generated_progressive_test_one_report.html', {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,
                'term_name': term.term_name,
                'gpa': round(float(total_gpa), 2),  # Round to 2 decimals
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

            # Fetch all scores for the student in the selected term (only for subjects assigned to student)
            scores = Score.objects.filter(
                student=student,
                term=term,
                subject__in=student.subjects.all()
            ).order_by('subject', '-updated_at').distinct('subject')

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

            # Calculate individual GPA scores for each subject and then average them
            individual_gpas = []
            for score in scores:
                if score.progressive_test_2_score is not None:
                    individual_gpas.append(get_gpa_from_progressive_test_2_score(score.progressive_test_2_score))

            # Calculate average GPA if there are any scores
            if individual_gpas:
                total_gpa = sum(individual_gpas) / len(individual_gpas)
            else:
                total_gpa = 0.00  # If no scores exist, default to 0 GPA

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
                'total_gpa': round(float(total_gpa), 2),  # Round to 2 decimals
                'scores': [
                    {
                        'subject': score.subject.name,
                        'progressive_test_2_score': round(float(score.progressive_test_2_score), 2),  # Round to 2 decimals
                        'grade': get_grade_from_progressive_test_2_score(score.progressive_test_2_score),
                        'gpa': round(get_gpa_from_progressive_test_2_score(score.progressive_test_2_score), 2)  # Round to 2 decimals
                    }
                    for score in scores
                ]
            }

            # Render the HTML for the report using the 'generated_progressive_test_two_report.html' template
            report_html = render_to_string('generated_progressive_test_two_report.html', {
                'student_name': student.fullname,
                'class_year': class_year_obj.name,
                'term_name': term.term_name,
                'gpa': round(float(total_gpa), 2),  # Round to 2 decimals
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
def view_end_of_term_scores(request, term_id=None, level_id=None, class_id=None):
    # Ensure that term_id, level_id, and class_id are provided
    if not term_id or not level_id or not class_id:
        return JsonResponse({'error': 'Term, Level, and Class are required'}, status=400)

    try:
        # Fetch the term, level, and class year objects based on provided ids
        term = Term.objects.get(id=term_id)
        level = Level.objects.get(id=level_id)
        class_year = ClassYear.objects.get(id=class_id, level=level)  # Ensure ClassYear belongs to Level

        # Fetch all scores for the selected term, level, and class year
        scores = Score.objects.filter(term=term, student__class_year=class_year)

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

        # Sort students alphabetically by name
        students_list.sort(key=lambda x: x['student_name'].lower())

        return JsonResponse({
            'students': students_list,
            'term': term.term_name,
            "term_id": term.id,
            "level_id": level.id,
            "class_year_id": class_year.id,
        })

    except Term.DoesNotExist:
        return JsonResponse({'error': 'Invalid term provided'}, status=404)
    except Level.DoesNotExist:
        return JsonResponse({'error': 'Invalid level provided'}, status=404)
    except ClassYear.DoesNotExist:
        return JsonResponse({'error': 'Invalid class year provided'}, status=404)





# Viewing Saved Midterm Scores by Term:
@login_required(login_url='login')
def view_midterm_scores(request, term_id=None, level_id=None, class_id=None):
    # Ensure that term_id, level_id, and class_id are provided
    if not term_id or not level_id or not class_id:
        return JsonResponse({'error': 'Term, Level, and Class are required'}, status=400)
    try:
        # Fetch the term, level, and class year objects based on provided ids
        term = Term.objects.get(id=term_id)
        level = Level.objects.get(id=level_id)
        class_year = ClassYear.objects.get(id=class_id, level=level)  # Ensure ClassYear belongs to Level

        # Fetch all scores for the selected term, level, and class year
        scores = Score.objects.filter(term=term, student__class_year=class_year)

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

        # Sort students alphabetically by name
        students_list.sort(key=lambda x: x['student_name'].lower())

        return JsonResponse({
            'students': students_list,
            'term': term.term_name,
            "term_id": term.id,
            "level_id": level.id,
            "class_year_id": class_year.id,
        })

    except Term.DoesNotExist:
        return JsonResponse({'error': 'Invalid term provided'}, status=404)
    except Level.DoesNotExist:
        return JsonResponse({'error': 'Invalid level provided'}, status=404)
    except ClassYear.DoesNotExist:
        return JsonResponse({'error': 'Invalid class year provided'}, status=404)




# Viewing Saved Mock Scores by Term:
@login_required(login_url='login')
def view_mock_scores(request, term_id=None, level_id=None, class_id=None):
    # Ensure that term_id, level_id, and class_id are provided
    if not term_id or not level_id or not class_id:
        return JsonResponse({'error': 'Term, Level, and Class are required'}, status=400)

    try:
        # Fetch the term, level, and class year objects based on provided ids
        term = Term.objects.get(id=term_id)
        level = Level.objects.get(id=level_id)
        class_year = ClassYear.objects.get(id=class_id, level=level)  # Ensure ClassYear belongs to Level

        # Fetch all scores for the selected term, level, and class year
        scores = Score.objects.filter(term=term, student__class_year=class_year)

        # Prepare a dictionary of student scores by subject
        students_data = {}

        # Function to calculate grade from total mock score
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

        # Function to calculate GPA from total mock score
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
            score_gpa = get_gpa_from_total_score(score.mock_score)
            grade = get_grade_from_total_score(score.mock_score)

            students_data[student_id]['scores'].append({
                'subject_name': subject_name,
                'mock_score': float(score.mock_score),
                'score_gpa': float(score_gpa),
                'grade': grade,
                'score_id': score.id
            })

            # Accumulate the total score and GPA for the student
            students_data[student_id]['total_score'] += score.mock_score
            students_data[student_id]['final_gpa'] += score_gpa

        # After populating data, calculate final grade and final GPA
        for student_id, data in students_data.items():
            total_score = data['total_score']
            total_score_percentage = total_score  # We can directly use total_score here

            data['final_gpa'] = data['final_gpa']  # Final GPA is accumulated GPA across all subjects

        # Include term in the JSON response
        students_list = list(students_data.values())

        # Sort students alphabetically by name
        students_list.sort(key=lambda x: x['student_name'].lower())

        return JsonResponse({
            'students': students_list,
            'term': term.term_name,
            "term_id": term.id,
            "level_id": level.id,
            "class_year_id": class_year.id,
        })

    except Term.DoesNotExist:
        return JsonResponse({'error': 'Invalid term provided'}, status=404)
    except Level.DoesNotExist:
        return JsonResponse({'error': 'Invalid level provided'}, status=404)
    except ClassYear.DoesNotExist:
        return JsonResponse({'error': 'Invalid class year provided'}, status=404)




# Viewing Saved Progressive Test One Scores by Term:
@login_required(login_url='login')
def view_progressive_one_test_scores(request, term_id=None, level_id=None, class_id=None):
    # Ensure that term_id, level_id, and class_id are provided
    if not term_id or not level_id or not class_id:
        return JsonResponse({'error': 'Term, Level, and Class are required'}, status=400)

    try:
        # Fetch the term, level, and class year objects based on provided ids
        term = Term.objects.get(id=term_id)
        level = Level.objects.get(id=level_id)
        class_year = ClassYear.objects.get(id=class_id, level=level)  # Ensure ClassYear belongs to Level

        # Fetch all scores for the selected term, level, and class year
        scores = Score.objects.filter(term=term, student__class_year=class_year)

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
                'progressive_test_1_score': float(progressive_test_1_score),
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

        # Sort students alphabetically by name
        students_list.sort(key=lambda x: x['student_name'].lower())

        return JsonResponse({
            'students': students_list,
            'term': term.term_name,
            "term_id": term.id,
            "level_id": level.id,
            "class_year_id": class_year.id,
        })

    except Term.DoesNotExist:
        return JsonResponse({'error': 'Invalid term provided'}, status=404)
    except Level.DoesNotExist:
        return JsonResponse({'error': 'Invalid level provided'}, status=404)
    except ClassYear.DoesNotExist:
        return JsonResponse({'error': 'Invalid class year provided'}, status=404)



# Viewing Saved Progressive Test Two Scores by Term:
@login_required(login_url='login')
def view_progressive_two_test_scores(request, term_id=None, level_id=None, class_id=None):
    # Ensure that term_id, level_id, and class_id are provided
    if not term_id or not level_id or not class_id:
        return JsonResponse({'error': 'Term, Level, and Class are required'}, status=400)

    try:
        # Fetch the term, level, and class year objects based on provided ids
        term = Term.objects.get(id=term_id)
        level = Level.objects.get(id=level_id)
        class_year = ClassYear.objects.get(id=class_id, level=level)  # Ensure ClassYear belongs to Level

        # Fetch all scores for the selected term, level, and class year
        scores = Score.objects.filter(term=term, student__class_year=class_year)

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
                'progressive_test_2_score': float(progressive_test_2_score),
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

        # Sort students alphabetically by name
        students_list.sort(key=lambda x: x['student_name'].lower())

        return JsonResponse({
            'students': students_list,
            'term': term.term_name,
            "term_id": term.id,
            "level_id": level.id,
            "class_year_id": class_year.id,
        })

    except Term.DoesNotExist:
        return JsonResponse({'error': 'Invalid term provided'}, status=404)
    except Level.DoesNotExist:
        return JsonResponse({'error': 'Invalid level provided'}, status=404)
    except ClassYear.DoesNotExist:
        return JsonResponse({'error': 'Invalid class year provided'}, status=404)


# Viewing Saved Progressive Test Three Scores by Term:
@login_required(login_url='login')
def view_progressive_three_test_scores(request, term_id=None, level_id=None, class_id=None):
    # Ensure that term_id, level_id, and class_id are provided
    if not term_id or not level_id or not class_id:
        return JsonResponse({'error': 'Term, Level, and Class are required'}, status=400)

    try:
        # Fetch the term, level, and class year objects based on provided ids
        term = Term.objects.get(id=term_id)
        level = Level.objects.get(id=level_id)
        class_year = ClassYear.objects.get(id=class_id, level=level)  # Ensure ClassYear belongs to Level

        # Fetch all scores for the selected term, level, and class year
        scores = Score.objects.filter(term=term, student__class_year=class_year)

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
                'progressive_test_3_score': float(progressive_test_3_score),
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

        # Sort students alphabetically by name
        students_list.sort(key=lambda x: x['student_name'].lower())

        return JsonResponse({
            'students': students_list,
            'term': term.term_name,
            "term_id": term.id,
            "level_id": level.id,
            "class_year_id": class_year.id,
        })

    except Term.DoesNotExist:
        return JsonResponse({'error': 'Invalid term provided'}, status=404)
    except Level.DoesNotExist:
        return JsonResponse({'error': 'Invalid level provided'}, status=404)
    except ClassYear.DoesNotExist:
        return JsonResponse({'error': 'Invalid class year provided'}, status=404)
