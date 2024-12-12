from django.contrib import admin
from .models import Level, ClassYear, Term, Subject, Student, Score, AcademicReport

# Register the Level model
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Level, LevelAdmin)

# Register the ClassYear model
class ClassYearAdmin(admin.ModelAdmin):
    list_display = ('level', 'name')
    search_fields = ('name',)
    list_filter = ('level',)

admin.site.register(ClassYear, ClassYearAdmin)

# Register the Term model
class TermAdmin(admin.ModelAdmin):
    list_display = ('term_name', 'class_year')
    search_fields = ('term_name', 'class_year__name')
    list_filter = ('term_name',)

admin.site.register(Term, TermAdmin)

# Register the Subject model
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter=('class_year',)

admin.site.register(Subject, SubjectAdmin)

# Register the Student model
class StudentAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'class_year')
    search_fields = ('fullname', 'class_year__name')
    list_filter = ('class_year',)
    filter_horizontal = ('subjects',)

admin.site.register(Student, StudentAdmin)

# Register the Score model
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'term', 'continuous_assessment', 'exam_score', 'total_score', 'grade')
    search_fields = ('student__fullname', 'subject__name', 'term__term_name')
    list_filter = ('term', 'subject','created_by')

admin.site.register(Score, ScoreAdmin)

# Register the AcademicReport model
class AcademicReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'student_gpa')
    search_fields = ('student__fullname', 'term__term_name')
    list_filter = ('term',)

admin.site.register(AcademicReport, AcademicReportAdmin)
