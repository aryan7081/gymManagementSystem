# Generated by Django 5.2.3 on 2025-06-20 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreFit', '0006_customuser_profile_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershipplan',
            name='features',
            field=models.JSONField(default=list),
        ),
    ]
