# Generated by Django 5.1.3 on 2024-12-01 00:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classyear',
            name='level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level', to='reports.level'),
        ),
        migrations.AlterField(
            model_name='score',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='reports.student'),
        ),
        migrations.AlterField(
            model_name='score',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='reports.subject'),
        ),
        migrations.AlterField(
            model_name='score',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='reports.term'),
        ),
        migrations.AlterField(
            model_name='student',
            name='class_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='reports.classyear'),
        ),
        migrations.AlterField(
            model_name='student',
            name='subjects',
            field=models.ManyToManyField(related_name='students', to='reports.subject'),
        ),
        migrations.AlterField(
            model_name='term',
            name='class_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='term', to='reports.classyear'),
        ),
    ]
