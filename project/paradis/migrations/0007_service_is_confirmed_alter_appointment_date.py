# Generated by Django 4.2.6 on 2023-11-30 20:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paradis', '0006_appointment_date_alter_appointment_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.date(2023, 11, 30)),
        ),
    ]
