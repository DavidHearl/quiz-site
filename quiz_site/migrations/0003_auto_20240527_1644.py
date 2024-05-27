# Generated by Django 3.2.21 on 2024-05-27 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0002_auto_20240526_2041'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='multiplechoice',
            name='question',
        ),
        migrations.RemoveField(
            model_name='picturequestion',
            name='question',
        ),
        migrations.RemoveField(
            model_name='truefalsequestion',
            name='question',
        ),
        migrations.AddField(
            model_name='questioncategory',
            name='category_question',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='multiplechoice',
            name='choice_1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='multiplechoice',
            name='choice_2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='multiplechoice',
            name='choice_3',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='multiplechoice',
            name='choice_4',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='picturequestion',
            name='choice_1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='picturequestion',
            name='choice_2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='picturequestion',
            name='choice_3',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='picturequestion',
            name='choice_4',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='GeneralKnowledge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=128)),
                ('answer', models.CharField(max_length=100)),
                ('difficulty', models.FloatField()),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz_site.questioncategory')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz_site.user')),
            ],
        ),
    ]
