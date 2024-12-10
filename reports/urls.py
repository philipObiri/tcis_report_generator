from django.urls import path
from . import views

urlpatterns = [
    # Main view for class information and rendering forms
    path('', views.custom_login, name='login'),

    path('reports/scores/delete-score/<int:score_id>/', views.delete_score, name='delete_score'),

    path('reports/', views.process_scores_view, name='process_scores'),

    path('reports/generate_report/', views.generate_report, name='generate_report'),

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
]
