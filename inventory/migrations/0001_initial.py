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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('division_id', models.CharField(max_length=150, db_index=True)),
                ('name', models.CharField(max_length=500)),
                ('json', jsonfield.fields.JSONField(default={})),
                ('custom_properties', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('source_url', models.URLField(max_length=500, unique=True)),
                ('extras', jsonfield.fields.JSONField(default={})),
                ('extras_keys', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('title', models.TextField(default='')),
                ('description', models.TextField(default='')),
                ('issued', models.DateTimeField(null=True)),
                ('modified', models.DateTimeField(null=True)),
                ('language', models.TextField(default='')),
                ('publisher', models.TextField(default='')),
                ('accrualPeriodicity', models.TextField(default='')),
                ('identifier', models.TextField(default='')),
                ('spatial', models.TextField(default='')),
                ('theme', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('keyword', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('contactPoint', models.TextField(default='')),
                ('landingPage', models.URLField(max_length=500, default='')),
                ('maintainer', models.TextField(default='')),
                ('maintainer_email', models.EmailField(max_length=75, default='')),
                ('author', models.TextField(default='')),
                ('author_email', models.EmailField(max_length=75, default='')),
                ('type', models.TextField(default='')),
                ('accessLevel', models.TextField(default='')),
                ('isopen', models.NullBooleanField()),
                ('license_id', models.TextField(default='')),
                ('license_url', models.URLField(default='')),
                ('license_title', models.TextField(default='')),
                ('license', models.URLField(db_index=True, default='')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('_id', models.TextField(default='')),
                ('json', jsonfield.fields.JSONField(default={})),
                ('custom_properties', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('division_id', models.CharField(max_length=150, db_index=True)),
                ('title', models.TextField(default='')),
                ('description', models.TextField(default='')),
                ('issued', models.DateTimeField(null=True)),
                ('modified', models.DateTimeField(null=True)),
                ('license', models.URLField(db_index=True, default='')),
                ('accessURL', models.URLField(max_length=2000, default='')),
                ('byteSize', models.BigIntegerField(null=True)),
                ('format', models.TextField(default='')),
                ('mimetype', models.TextField(default='')),
                ('mimetype_inner', models.TextField(default='')),
                ('mediaType', models.TextField(db_index=True, default='')),
                ('validation_errors', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('validation_encoding', models.TextField(null=True)),
                ('validation_headers', models.TextField(null=True)),
                ('validation_content_type', models.TextField(null=True)),
                ('validation_extension', models.TextField(null=True)),
                ('valid', models.NullBooleanField()),
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
            unique_together=set([('division_id', 'name')]),
        ),
    ]
