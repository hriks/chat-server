# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-29 19:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_thread_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='date',
            new_name='time',
        ),
    ]
