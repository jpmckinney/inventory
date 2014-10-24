# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_auto_20141023_1103'),
    ]

    operations = [
        migrations.RenameField(
            model_name='package',
            old_name='notes',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='package',
            old_name='_id',
            new_name='identifier',
        ),
        migrations.RenameField(
            model_name='package',
            old_name='metadata_created',
            new_name='issued',
        ),
        migrations.RenameField(
            model_name='package',
            old_name='tags',
            new_name='keyword',
        ),
        migrations.RenameField(
            model_name='package',
            old_name='url',
            new_name='landingPage',
        ),
        migrations.RenameField(
            model_name='package',
            old_name='metadata_modified',
            new_name='modified',
        ),
        migrations.RenameField(
            model_name='package',
            old_name='owner_org',
            new_name='publisher',
        ),
    ]
