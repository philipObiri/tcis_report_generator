from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Level, ClassYear,
    Term, Subject, Student,TeacherProfile,
    Score, AcademicReport, StudentReportComment, MockReportComment
    # MidtermReport,
    # ProgressiveTestOneReport, ProgressiveTestTwoReport,
    # ProgressiveTestThreeReport
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
    list_display = ('name', 'grading_system', 'get_class_years')
    search_fields = ('name',)
    list_filter = ('grading_system', 'class_year',)
    filter_horizontal = ('class_year',)

    def get_class_years(self, obj):
        return ", ".join([cy.name for cy in obj.class_year.all()])
    get_class_years.short_description = 'Class Years'



# Register the Student model
class StudentAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'class_year')
    search_fields = ('fullname', 'class_year__name')
    list_filter = ('class_year',)
    filter_horizontal = ('subjects',)



# TeacherProfile Admin
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_subjects', 'get_class_years')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('subjects',)
    filter_horizontal = ('subjects',)
    
    def get_subjects(self, obj):
        return ", ".join([subject.name for subject in obj.subjects.all()])
    get_subjects.short_description = 'Subjects'

    def get_class_years(self, obj):
        class_years = set()
        for subject in obj.subjects.all():
            for class_year in subject.class_year.all():
                class_years.add(class_year.name)  # Assuming 'name' is a field of ClassYear
        return ", ".join(class_years)
    get_class_years.short_description = 'Class Years'




# Register the Score model
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'get_grading_system', 'term', 'class_work_score', 'progressive_test_1_score',
                    'progressive_test_2_score', 'midterm_score','mock_score', 'exam_score',
                    'continuous_assessment', 'total_score', 'grade')
    search_fields = ('student__fullname', 'subject__name', 'term__term_name')
    list_filter = ('term', 'subject', 'subject__grading_system', 'created_by')
    readonly_fields = ('continuous_assessment', 'total_score', 'grade', 'get_grading_system')

    def get_grading_system(self, obj):
        return obj.subject.get_grading_system_display() if obj.subject else 'N/A'
    get_grading_system.short_description = 'Grading System'





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







# Register the StudentReportComment model
class StudentReportCommentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_year', 'term', 'has_academic_comment', 'has_behavioral_comment', 'created_by', 'updated_at')
    search_fields = ('student__fullname', 'class_year__name', 'term__term_name')
    list_filter = ('class_year', 'term', 'created_by')
    readonly_fields = ('created_at', 'updated_at')

    def has_academic_comment(self, obj):
        return bool(obj.academic_comment)
    has_academic_comment.boolean = True
    has_academic_comment.short_description = 'Academic'

    def has_behavioral_comment(self, obj):
        return bool(obj.behavioral_comment)
    has_behavioral_comment.boolean = True
    has_behavioral_comment.short_description = 'Behavioral'


# Register the MockReportComment model
class MockReportCommentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_year', 'term', 'has_academic_comment', 'has_behavioral_comment', 'created_by', 'updated_at')
    search_fields = ('student__fullname', 'class_year__name', 'term__term_name')
    list_filter = ('class_year', 'term', 'created_by')
    readonly_fields = ('created_at', 'updated_at')

    def has_academic_comment(self, obj):
        return bool(obj.academic_comment)
    has_academic_comment.boolean = True
    has_academic_comment.short_description = 'Academic'

    def has_behavioral_comment(self, obj):
        return bool(obj.behavioral_comment)
    has_behavioral_comment.boolean = True
    has_behavioral_comment.short_description = 'Behavioral'


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
admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(StudentReportComment, StudentReportCommentAdmin)
admin.site.register(MockReportComment, MockReportCommentAdmin)
# admin.site.register(MidtermReport, MidtermReportAdmin)
# admin.site.register(ProgressiveTestOneReport, ProgressiveTestOneReportAdmin)
# admin.site.register(ProgressiveTestTwoReport, ProgressiveTestTwoReportAdmin)
# admin.site.register(ProgressiveTestThreeReport, ProgressiveTestThreeReportAdmin)
admin.site.register(AcademicReport, AcademicReportAdmin)