# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import gc

from django.db import migrations


def migrate_keyword(apps, schema_editor):
    # https://djangosnippets.org/snippets/1949/
    def queryset_iterator(queryset, chunksize=1000):
        pk = 0
        last_pk = queryset.order_by('-pk')[0].pk
        queryset = queryset.order_by('pk')
        while pk < last_pk:
            for row in queryset.filter(pk__gt=pk)[:chunksize]:
                pk = row.pk
                yield row
            gc.collect()

    Dataset = apps.get_model('inventory', 'Dataset')

    for dataset in queryset_iterator(Dataset.objects.filter(temporary_keyword=None)):
        if dataset.keyword:
            dataset.temporary_keyword = [keyword['name'] for keyword in dataset.keyword]
            dataset.save()


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_dataset_temporary_keyword'),
    ]

    operations = [
        migrations.RunPython(migrate_keyword),
    ]
