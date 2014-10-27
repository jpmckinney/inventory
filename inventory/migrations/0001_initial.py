# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('country_code', models.CharField(max_length=2, db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('json', jsonfield.fields.JSONField(default={})),
                ('custom_properties', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('source_url', models.URLField(unique=True)),
                ('extras', jsonfield.fields.JSONField(default={})),
                ('extras_keys', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('title', models.TextField(default='')),
                ('description', models.TextField(default='')),
                ('issued', models.DateTimeField(null=True)),
                ('modified', models.DateTimeField(null=True)),
                ('publisher', models.TextField(default='')),
                ('identifier', models.TextField(default='')),
                ('keyword', jsonfield.fields.JSONField(default={})),
                ('maintainer', models.TextField(default='')),
                ('maintainer_email', models.EmailField(max_length=75, default='')),
                ('author', models.TextField(default='')),
                ('author_email', models.EmailField(max_length=75, default='')),
                ('landingPage', models.URLField(max_length=500, default='')),
                ('isopen', models.NullBooleanField()),
                ('license_id', models.TextField(default='')),
                ('license_url', models.URLField(default='')),
                ('license_title', models.TextField(default='')),
                ('license', models.URLField(default='', db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('_id', models.TextField(default='')),
                ('json', jsonfield.fields.JSONField(default={})),
                ('custom_properties', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('country_code', models.CharField(max_length=2, db_index=True)),
                ('mimetype', models.TextField(default='')),
                ('mimetype_inner', models.TextField(default='')),
                ('title', models.TextField(default='')),
                ('description', models.TextField(default='')),
                ('issued', models.DateTimeField(null=True)),
                ('modified', models.DateTimeField(null=True)),
                ('accessURL', models.URLField(max_length=2000, default='')),
                ('byteSize', models.BigIntegerField(null=True)),
                ('format', models.TextField(default='')),
                ('mediaType', models.TextField(default='', db_index=True)),
                ('dataset', models.ForeignKey(to='inventory.Dataset')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='distribution',
            unique_together=set([('dataset', '_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='dataset',
            unique_together=set([('country_code', 'name')]),
        ),
    ]
