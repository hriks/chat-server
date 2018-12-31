# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-29 17:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='user',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='users',
        ),
        migrations.AddField(
            model_name='message',
            name='profile',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='chat.Profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='thread',
            name='profiles',
            field=models.ManyToManyField(related_name='threads', to='chat.Profile'),
        ),
    ]
