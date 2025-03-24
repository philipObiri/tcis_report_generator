from django.urls import path
from . import views

urlpatterns = [
    # Main view for class information and rendering forms
    path('', views.custom_login, name='login'),
    path('dashboard/scores-entry/select-option/', views.select_option, name='select_option'),
    path('dashboard/progressive-test-scores/entry-options/', views.select_progressive_option, name="select_progressive_option"),
    path('dashboard/entries/class-scores/', views.class_scores, name="class_scores"),
    path('dashboard/entries/midterm-scores/', views.midterm_scores, name="midterm"),

    path('dashboard/entries/mock-scores/', views.mock_scores, name="mock_scores"),

    path('dashboard/entries/first-progressive-scores/', views.progressive_test_scores_one, name="progressive_score_one"),
    path('dashboard/entries/second-progressive-scores/', views.progressive_test_scores_two, name="progressive_score_two"),
    path('third-progressive-scores/', views.progressive_test_scores_three, name="progressive_score_three"),




    # Endpoints For Viewing Saved Scores :
    path('dashboard/entries/view_midterm_scores/<int:term_id>/', views.view_midterm_scores, name='view_midterm_scores'),
    path('dashboard/entries/view_mock_scores/<int:term_id>/', views.view_mock_scores, name='view_mock_scores'),
    path('dashboard/entries/view_end_of_term_scores/<int:term_id>/', views.view_end_of_term_scores, name='view_end_of_term_scores'),
    path('dashboard/entries/view_progressive_one_test_scores/<int:term_id>/', views.view_progressive_one_test_scores, name='view_progressive_one_test_scores'),
    path('dashboard/entries/view_progressive_two_test_scores/<int:term_id>/', views.view_progressive_two_test_scores, name='view_progressive_two_test_scores'),
    path('dashboard/entries/view_progressive_three_test_scores/<int:term_id>/', views.view_progressive_three_test_scores, name='view_progressive_three_test_scores'),


    path('reports/scores/delete-score/<int:score_id>/', views.delete_score, name='delete_score'),
    path('reports/', views.process_scores_view, name='process_scores'),
    path('reports/generate_report/', views.generate_report, name='generate_report'),
    path('reports/generate_midterm_report/', views.generate_midterm_report, name="generate_midterm_report"),
    path('reports/generate_mock_report/', views.generate_mock_report, name="generate_mock_report"),
    path('reports/generate_progressive_one_report/', views.generate_progressive_one_report, name="generate_progressive_one_report"),

    # Endpoint to get classes based on the selected level
    path('get-classes-by-level/<int:level_id>/', views.get_classes_by_level, name='get_classes_by_level'),

    # Endpoint to get terms based on the selected class/year
    path('get-terms-by-class-year/<int:class_year_id>/', views.get_terms_by_class_year, name='get_terms_by_class_year'),

    # Endpoint to get subjects based on the selected class/year
    path('get-subjects-by-class-year/<int:class_year_id>/', views.get_subjects_by_class_year, name='get_subjects_by_class_year'),

    # Endpoint to fetch students and their formset based on selected filters
    path('get-students-by-filters/<int:level_id>/<int:class_year_id>/<int:term_id>/<int:subject_id>/', 
         views.get_students_by_filters, name='get_students_by_filters'),

    path('get-levels/', views.get_levels, name='get_levels'),

    path('logout/', views.custom_logout, name='logout'),

    path('reports/get_report_details/<int:student_id>/<int:term_id>/', views.view_academic_report, name='view_academic_report'),
    path('reports/get_midterm_report_details/<int:student_id>/<int:term_id>/', views.view_midterm_report, name='view_midterm_report'),
    path('reports/get_mock_report_details/<int:student_id>/<int:term_id>/', views.view_mock_report, name='view_mock_report'),
    path('reports/get_progessive_one_report_details/<int:student_id>/<int:term_id>/', views.view_progressive_test_score_one_report, name='view_progressive_one_report'),
    path('reports/get_progessive_two_report_details/<int:student_id>/<int:term_id>/', views.view_progressive_test_score_two_report, name='view_progressive_two_report'),
    path('reports/get_progessive_three_report_details/<int:student_id>/<int:term_id>/', views.view_progressive_test_score_three_report, name='view_progressive_three_report'),
]
