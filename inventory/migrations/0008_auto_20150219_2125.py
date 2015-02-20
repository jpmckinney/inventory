# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_distribution_http_status_code'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='distribution',
            index_together=set([('dataset', 'mediaType')]),
        ),
    ]
