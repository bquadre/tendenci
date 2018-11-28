# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-19 16:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_auto_20180724_1308'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='facebook',
            field=models.URLField(blank=True, default='', verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='profile',
            name='instagram',
            field=models.URLField(blank=True, default='', verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='profile',
            name='linkedin',
            field=models.URLField(blank=True, default='', verbose_name='LinkedIn'),
        ),
        migrations.AddField(
            model_name='profile',
            name='twitter',
            field=models.URLField(blank=True, default='', verbose_name='Twitter'),
        ),
        migrations.AddField(
            model_name='profile',
            name='youtube',
            field=models.URLField(blank=True, default='', verbose_name='YouTube'),
        ),
    ]