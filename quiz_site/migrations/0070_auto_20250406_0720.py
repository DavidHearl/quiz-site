# Generated by Django 3.2.25 on 2025-04-06 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0069_quiz_join_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='join_code',
        ),
        migrations.AddField(
            model_name='quiz',
            name='countdown_start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
