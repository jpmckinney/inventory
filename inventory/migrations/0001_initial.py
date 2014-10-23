# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields
import jsonfield.fields
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('country_code', models.CharField(max_length=2)),
                ('source_url', models.URLField(unique=True)),
                ('name', models.CharField(max_length=100)),
                ('json', jsonfield.fields.JSONField()),
                ('custom_properties', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('extras_keys', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('title', models.TextField(default='')),
                ('notes', models.TextField(default='')),
                ('metadata_created', models.DateTimeField()),
                ('metadata_modified', models.DateTimeField()),
                ('owner_org', models.TextField(default='')),
                ('_id', uuidfield.fields.UUIDField(max_length=32)),
                ('tags', jsonfield.fields.JSONField()),
                ('maintainer', models.TextField(default='')),
                ('maintainer_email', models.EmailField(max_length=75, default='')),
                ('author', models.TextField(default='')),
                ('author_email', models.EmailField(max_length=75, default='')),
                ('url', models.URLField(max_length=500, default='')),
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
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('_id', uuidfield.fields.UUIDField(unique=True, max_length=32)),
                ('json', jsonfield.fields.JSONField()),
                ('custom_properties', djorm_pgarray.fields.ArrayField(dbtype='text')),
                ('name', models.TextField(default='')),
                ('description', models.TextField(default='')),
                ('created', models.DateTimeField()),
                ('last_modified', models.DateTimeField()),
                ('url', models.URLField(default='')),
                ('size', models.BigIntegerField()),
                ('mimetype', models.TextField(default='')),
                ('format', models.TextField(default='')),
                ('package', models.ForeignKey(to='inventory.Package')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='package',
            unique_together=set([('country_code', 'name')]),
        ),
    ]
