# Generated by Django 3.2.21 on 2024-11-27 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0050_player_question_answered'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='page_updates',
            field=models.IntegerField(default=0),
        ),
    ]