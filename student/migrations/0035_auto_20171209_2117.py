# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-12-09 20:17
from __future__ import unicode_literals

from django.db import migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0034_auto_20171209_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='cropping',
            field=image_cropping.fields.ImageRatioField('photo', '430x430', adapt_rotation=False, allow_fullsize=False, free_crop=False, help_text=None, hide_image_field=False, size_warning=True, verbose_name='cropping'),
        ),
    ]
