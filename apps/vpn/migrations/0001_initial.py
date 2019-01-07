# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-07 03:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VPNUsageDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='VPN使用说明', max_length=255, verbose_name='标题')),
                ('content', models.TextField(default='', verbose_name='说明内容')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
            ],
            options={
                'verbose_name': 'VPN使用说明',
                'verbose_name_plural': 'VPN使用说明',
            },
        ),
    ]
