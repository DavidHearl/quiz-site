# Generated by Django 3.2.21 on 2024-06-21 10:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0033_questions_quiz'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz_site.quiz'),
        ),
    ]
