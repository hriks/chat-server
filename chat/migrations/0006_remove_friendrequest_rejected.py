# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-31 05:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_thread_last_message_read'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friendrequest',
            name='rejected',
        ),
    ]
