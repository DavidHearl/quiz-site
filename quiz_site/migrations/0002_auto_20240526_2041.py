# Generated by Django 3.2.25 on 2024-05-26 19:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='multiplechoice',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz_site.questioncategory'),
        ),
        migrations.AddField(
            model_name='picturequestion',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz_site.questioncategory'),
        ),
        migrations.AddField(
            model_name='truefalsequestion',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz_site.questioncategory'),
        ),
        migrations.AlterField(
            model_name='user',
            name='player_score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
