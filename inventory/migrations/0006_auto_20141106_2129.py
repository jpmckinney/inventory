# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_remove_dataset_keyword'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataset',
            old_name='temporary_keyword',
            new_name='keyword',
        ),
    ]
