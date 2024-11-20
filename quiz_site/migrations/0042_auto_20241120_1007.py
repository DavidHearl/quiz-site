# Generated by Django 3.2.21 on 2024-11-20 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0041_quiz_random_numbers'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='round1_set',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='quiz',
            name='round2_set',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='quiz',
            name='round3_set',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='quiz',
            name='round4_set',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='quiz',
            name='round5_set',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='quiz',
            name='round6_set',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='quiz',
            name='round7_set',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='quiz',
            name='round8_set',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
