# Generated by Django 3.2.21 on 2024-06-11 11:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0012_jets'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jets',
            name='code_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='Celebrities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='')),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('difficulty', models.FloatField(blank=True, null=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz_site.questioncategory')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz_site.user')),
            ],
        ),
    ]
