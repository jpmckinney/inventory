# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20150215_2250'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 2, 15, 23, 18, 47, 132643)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dataset',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2015, 2, 15, 23, 18, 51, 156542)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='distribution',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 2, 15, 23, 18, 57, 748349)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='distribution',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2015, 2, 15, 23, 19, 1, 244244)),
            preserve_default=False,
        ),
    ]
