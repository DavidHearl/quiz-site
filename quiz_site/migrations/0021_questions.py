# Generated by Django 3.2.21 on 2024-06-18 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0020_remove_generalknowledge_choice_4'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type', models.CharField(max_length=100)),
                ('question', models.CharField(max_length=100)),
            ],
        ),
    ]