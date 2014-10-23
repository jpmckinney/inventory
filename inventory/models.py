from django.db import models
from djorm_pgarray.fields import ArrayField
from jsonfield import JSONField
from uuidfield import UUIDField


class Package(models.Model):
    # Source
    country_code = models.CharField(max_length=2)
    source_url = models.URLField(unique=True, max_length=200)

    # Properties
    name = models.CharField(max_length=100)  # @see https://github.com/ckan/ckan/blob/master/ckan/model/package.py#L27
    json = JSONField()
    custom_properties = ArrayField(dbtype='text')
    extras_keys = ArrayField(dbtype='text')

    # dcat:Dataset
    title = models.TextField(default='')
    notes = models.TextField(default='')
    metadata_created = models.DateTimeField()
    metadata_modified = models.DateTimeField()
    owner_org = models.TextField(default='')
    _id = UUIDField()
    tags = JSONField()
    maintainer = models.TextField(default='')
    maintainer_email = models.EmailField(default='')
    author = models.TextField(default='')
    author_email = models.EmailField(default='')
    url = models.URLField(default='', max_length=500)  # 401 observed

    # License properties
    isopen = models.NullBooleanField()
    license_id = models.TextField(default='')
    license_url = models.URLField(default='')
    license_title = models.TextField(default='')

    class Meta:
        unique_together = (('country_code', 'name'),)


class Resource(models.Model):
    package = models.ForeignKey('Package')

    # Properties
    _id = UUIDField(unique=True)
    json = JSONField()
    custom_properties = ArrayField(dbtype='text')

    # dcat:Distribution
    name = models.TextField(default='')
    description = models.TextField(default='')
    created = models.DateTimeField(null=True)
    last_modified = models.DateTimeField(null=True)
    url = models.URLField(default='', max_length=500)  # 403 observed
    size = models.BigIntegerField(null=True)
    mimetype = models.TextField(default='')
    format = models.TextField(default='')
