# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='author',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='author_email',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='maintainer',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='maintainer_email',
        ),
        migrations.AddField(
            model_name='dataset',
            name='temporal',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
    ]
