# Generated by Django 5.1.7 on 2025-04-17 12:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_feedback_timestamp_feedback_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(condition=models.Q(('end_date__gt', models.F('start_date'))), name='check_start_date'),
        ),
    ]
