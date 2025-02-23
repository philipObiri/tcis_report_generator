from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Level, ClassYear, 
    Term, Subject, Student,
    Score, AcademicReport,MidtermReport, 
    ProgressiveTestOneReport, ProgressiveTestTwoReport, 
    ProgressiveTestThreeReport
)

# Register the Level model
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)



# Register the ClassYear model
class ClassYearAdmin(admin.ModelAdmin):
    list_display = ('level', 'name')
    search_fields = ('name',)
    list_filter = ('level',)



# Register the Term model
class TermAdmin(admin.ModelAdmin):
    list_display = ('term_name', 'class_year')
    search_fields = ('term_name', 'class_year__name')
    list_filter = ('term_name',)



# Register the Subject model
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('class_year',)
    filter_horizontal = ('class_year',)



# Register the Student model
class StudentAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'class_year')
    search_fields = ('fullname', 'class_year__name')
    list_filter = ('class_year',)
    filter_horizontal = ('subjects',)


# Register the Score model
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'term', 'class_work_score', 'progressive_test_1_score', 'progressive_test_2_score', 'progressive_test_3_score', 'midterm_score', 'exam_score', 'continuous_assessment', 'total_score', 'grade')
    search_fields = ('student__fullname', 'subject__name', 'term__term_name')
    list_filter = ('term', 'subject', 'created_by')
    readonly_fields = ('continuous_assessment', 'total_score', 'grade')  # Make these fields readonly as they are auto-calculated





# # Custom admin class for MidtermReport
# class MidtermReportAdmin(admin.ModelAdmin):
#     list_display = ('student', 'term', 'midterm_gpa', 'generated_by')
#     search_fields = ('student__fullname', 'term__term_name')
#     list_filter = ('term',)
#     readonly_fields = ('midterm_gpa', 'generated_by')


# # Custom admin class for ProgressiveTestOneReport
# class ProgressiveTestOneReportAdmin(admin.ModelAdmin):
#     list_display = ('student', 'term', 'progressive_test1_gpa', 'generated_by',)
#     search_fields = ('student__fullname', 'term__term_name')
#     list_filter = ('term',)
#     readonly_fields = ('progressive_test1_gpa', 'generated_by')


# # Custom admin class for ProgressiveTestTwoReport
# class ProgressiveTestTwoReportAdmin(admin.ModelAdmin):
#     list_display = ('student', 'term', 'progressive_test2_gpa', 'generated_by')
#     search_fields = ('student__fullname', 'term__term_name')
#     list_filter = ('term',)
#     readonly_fields = ('progressive_test2_gpa', 'generated_by')


# # Custom admin class for ProgressiveTestThreeReport
# class ProgressiveTestThreeReportAdmin(admin.ModelAdmin):
#     list_display = ('student', 'term', 'progressive_test3_gpa', 'generated_by')
#     search_fields = ('student__fullname', 'term__term_name')
#     list_filter = ('term',)
#     readonly_fields = ('progressive_test3_gpa', 'generated_by')







# Register the AcademicReport model
class AcademicReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'student_gpa')
    search_fields = ('student__fullname', 'term__term_name')
    list_filter = ('term',)





# Registering the models with custom admin classes
admin.site.register(Level, LevelAdmin)
admin.site.register(ClassYear, ClassYearAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Score, ScoreAdmin)
# admin.site.register(MidtermReport, MidtermReportAdmin)
# admin.site.register(ProgressiveTestOneReport, ProgressiveTestOneReportAdmin)
# admin.site.register(ProgressiveTestTwoReport, ProgressiveTestTwoReportAdmin)
# admin.site.register(ProgressiveTestThreeReport, ProgressiveTestThreeReportAdmin)
admin.site.register(AcademicReport, AcademicReportAdmin)