# Generated by Django 3.2.21 on 2024-12-12 12:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0055_player_player_scores'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='player_scores',
            new_name='points',
        ),
    ]
