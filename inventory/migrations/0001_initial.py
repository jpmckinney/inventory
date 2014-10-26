# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('country_code', models.CharField(max_length=2)),
                ('name', models.CharField(max_length=100)),
                ('json', jsonfield.fields.JSONField(default={})),
                ('custom_properties', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('source_url', models.URLField(unique=True)),
                ('extras_keys', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('title', models.TextField(default='')),
                ('description', models.TextField(default='')),
                ('issued', models.DateTimeField(null=True)),
                ('modified', models.DateTimeField(null=True)),
                ('publisher', models.TextField(default='')),
                ('identifier', models.TextField(default='')),
                ('keyword', jsonfield.fields.JSONField(default={})),
                ('maintainer', models.TextField(default='')),
                ('maintainer_email', models.EmailField(default='', max_length=75)),
                ('author', models.TextField(default='')),
                ('author_email', models.EmailField(default='', max_length=75)),
                ('landingPage', models.URLField(default='', max_length=500)),
                ('isopen', models.NullBooleanField()),
                ('license_id', models.TextField(default='')),
                ('license_url', models.URLField(default='')),
                ('license_title', models.TextField(default='')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('_id', models.TextField(default='')),
                ('json', jsonfield.fields.JSONField(default={})),
                ('custom_properties', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('name', models.TextField(default='')),
                ('description', models.TextField(default='')),
                ('created', models.DateTimeField(null=True)),
                ('last_modified', models.DateTimeField(null=True)),
                ('url', models.URLField(default='', max_length=2000)),
                ('size', models.BigIntegerField(null=True)),
                ('mimetype', models.TextField(default='')),
                ('format', models.TextField(default='')),
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
