# Generated by Django 5.1.3 on 2025-06-27 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0024_score_progressive_test_3_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicreport',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='midtermreport',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mockreport',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='progressivetestonereport',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='progressivetesttworeport',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
