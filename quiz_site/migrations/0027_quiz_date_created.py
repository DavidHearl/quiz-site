# Generated by Django 3.2.21 on 2024-06-20 10:06

import datetime
from django.db import migrations, models
from django.utils import timezone

class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0026_auto_20240619_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='date_created',
            field=models.DateTimeField(default=timezone.now),
        ),
    ]