# Generated by Django 5.1.3 on 2024-12-01 19:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0009_score_grade'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_gpa', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='academic_reports', to='reports.student')),
                ('student_score', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='academic_reports', to='reports.score')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='academic_reports', to='reports.term')),
            ],
        ),
    ]
