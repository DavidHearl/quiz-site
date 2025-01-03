# Generated by Django 3.2.25 on 2024-12-27 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0065_generalknowledgecategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalknowledge',
            name='category',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz_site.generalknowledgecategory'),
        ),
        migrations.AlterField(
            model_name='generalknowledgecategory',
            name='category',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
