# Generated by Django 3.2.21 on 2024-05-28 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_site', '0007_auto_20240528_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='guesstheflag',
            name='flag',
            field=models.ImageField(default=1, upload_to=''),
            preserve_default=False,
        ),
    ]
