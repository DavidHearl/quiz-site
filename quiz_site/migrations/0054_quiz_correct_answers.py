# Generated by Django 3.2.25 on 2024-12-07 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0053_auto_20241206_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='correct_answers',
            field=models.JSONField(default=dict),
        ),
    ]
