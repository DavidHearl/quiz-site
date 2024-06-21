# Generated by Django 3.2.21 on 2024-06-21 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0031_questions_general_knowledge_questions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questions',
            name='answer',
        ),
        migrations.RemoveField(
            model_name='questions',
            name='capital',
        ),
        migrations.RemoveField(
            model_name='questions',
            name='choice_1',
        ),
        migrations.RemoveField(
            model_name='questions',
            name='choice_2',
        ),
        migrations.RemoveField(
            model_name='questions',
            name='choice_3',
        ),
        migrations.RemoveField(
            model_name='questions',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='questions',
            name='date',
        ),
        migrations.RemoveField(
            model_name='questions',
            name='difficulty',
        ),
        migrations.RemoveField(
            model_name='questions',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='questions',
            name='question',
        ),
        migrations.AddField(
            model_name='questions',
            name='celebrity_questions',
            field=models.ManyToManyField(blank=True, to='quiz_site.Celebrities'),
        ),
        migrations.AddField(
            model_name='questions',
            name='flag_questions',
            field=models.ManyToManyField(blank=True, to='quiz_site.Flags'),
        ),
        migrations.AddField(
            model_name='questions',
            name='jet_questions',
            field=models.ManyToManyField(blank=True, to='quiz_site.Jets'),
        ),
        migrations.AddField(
            model_name='questions',
            name='location_questions',
            field=models.ManyToManyField(blank=True, to='quiz_site.Locations'),
        ),
        migrations.AddField(
            model_name='questions',
            name='logo_questions',
            field=models.ManyToManyField(blank=True, to='quiz_site.Logos'),
        ),
        migrations.AddField(
            model_name='questions',
            name='movie_questions',
            field=models.ManyToManyField(blank=True, to='quiz_site.Movies'),
        ),
        migrations.AddField(
            model_name='questions',
            name='true_or_false_questions',
            field=models.ManyToManyField(blank=True, to='quiz_site.TrueOrFalse'),
        ),
    ]