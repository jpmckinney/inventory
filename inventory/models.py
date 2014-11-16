from django.db import models
from djorm_pgarray.fields import ArrayField
from jsonfield import JSONField


class Dataset(models.Model):  # dcat:Dataset
    # Identification and common fields
    country_code = models.CharField(max_length=2, db_index=True)
    name = models.CharField(max_length=100)  # @see https://github.com/ckan/ckan/blob/master/ckan/model/package.py#L27
    json = JSONField(default={})
    custom_properties = ArrayField(dbtype='text')

    # Additional fields
    source_url = models.URLField(unique=True)
    extras = JSONField(default={})
    extras_keys = ArrayField(dbtype='text')

    # @see http://www.w3.org/TR/vocab-dcat/
    title = models.TextField(default='')  # dct
    description = models.TextField(default='')  # dct
    issued = models.DateTimeField(null=True)  # dct
    modified = models.DateTimeField(null=True)  # dct
    language = models.TextField(default='')  # dct
    publisher = models.TextField(default='')  # dct
    accrualPeriodicity = models.TextField(default='')  # dct
    identifier = models.TextField(default='')  # dct (not always a UUID)
    spatial = models.TextField(default='')  # dct
    theme = ArrayField(dbtype='text')  # dcat
    keyword = ArrayField(dbtype='text')  # dcat
    contactPoint = models.TextField(default='')  # dcat
    maintainer = models.TextField(default='')
    maintainer_email = models.EmailField(default='')
    author = models.TextField(default='')
    author_email = models.EmailField(default='')
    landingPage = models.URLField(default='', max_length=500)  # dcat (length 401 observed)

    # @see http://project-open-data.github.io/v1.1/schema/
    # @see http://project-open-data.github.io/v1.1/schema/#accessLevel
    accessLevel = models.TextField(default='')

    # License properties
    isopen = models.NullBooleanField()
    license_id = models.TextField(default='')
    license_url = models.URLField(default='')
    license_title = models.TextField(default='')

    # Clean properties
    license = models.URLField(default='', db_index=True)  # dct

    class Meta:
        unique_together = (('country_code', 'name'),)

    def __str__(self):
        return '{}: {}'.format(self.country_code, self.name)


class Distribution(models.Model):  # dcat:Distribution
    # Identification and common fields
    dataset = models.ForeignKey('Dataset')
    _id = models.TextField(default='')  # (not always a UUID)
    json = JSONField(default={})
    custom_properties = ArrayField(dbtype='text')

    # Additional fields
    country_code = models.CharField(max_length=2, db_index=True)

    # @see http://www.w3.org/TR/vocab-dcat/
    title = models.TextField(default='')  # dct
    description = models.TextField(default='')  # dct
    issued = models.DateTimeField(null=True)  # dct
    modified = models.DateTimeField(null=True)  # dct
    license = models.URLField(default='', db_index=True)  # dct
    accessURL = models.URLField(default='', max_length=2000)  # dcat (length 1692 observed)
    byteSize = models.BigIntegerField(null=True)  # dcat
    mimetype = models.TextField(default='')
    mimetype_inner = models.TextField(default='')
    format = models.TextField(default='')  # dct

    # Clean properties
    mediaType = models.TextField(default='', db_index=True)  # dcat

    # CSV validation
    validation_errors = models.TextField(null=True)
    validation_encoding = models.TextField(null=True)
    validation_headers = models.TextField(null=True)
    validation_content_type = models.TextField(null=True)
    validation_extension = models.TextField(null=True)
    valid = models.NullBooleanField(null=True)

    class Meta:
        unique_together = (('dataset', '_id'),)

    def __str__(self):
        return '{}: {} {}'.format(self.country_code, self.dataset, self._id)
