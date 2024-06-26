# Generated by Django 3.2.21 on 2024-05-27 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0004_picturequestion_question'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='picturequestion',
            name='question',
        ),
        migrations.AddField(
            model_name='truefalsequestion',
            name='question',
            field=models.CharField(default='Test', max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='multiplechoice',
            name='difficulty',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='picturequestion',
            name='difficulty',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='truefalsequestion',
            name='difficulty',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
