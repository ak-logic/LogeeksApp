# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-08-12 21:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0011_auto_20170906_2028'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('related_transaction', models.CharField(max_length=10)),
                ('tutor_involved', models.CharField(max_length=7)),
                ('student_involved', models.CharField(max_length=5)),
                ('title', models.CharField(max_length=50)),
                ('content', models.CharField(max_length=800)),
                ('read_status', models.BooleanField(default=False)),
                ('other_info', models.CharField(max_length=50)),
            ],
        ),
    ]
