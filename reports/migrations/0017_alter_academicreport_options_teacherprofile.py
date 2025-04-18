# Generated by Django 4.2.16 on 2025-02-24 12:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reports', '0016_alter_academicreport_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='academicreport',
            options={'verbose_name': 'End of Term Report', 'verbose_name_plural': 'End of Term Reports'},
        ),
        migrations.CreateModel(
            name='TeacherProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subjects', models.ManyToManyField(related_name='teachers', to='reports.subject')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
