# Catalog structure

from django.db.models import Count

from inventory.models import Dataset, Distribution

datasets = Dataset.objects
distributions = Distribution.objects

division_ids = set(distributions.values_list('division_id', flat=True))
counts = datasets.values('division_id', 'id').annotate(count=Count('distribution'))

# Catalogs with datasets without distributions.
zero = set(map(lambda x: x['division_id'], counts.filter(count=0))) & division_ids

# Sample datasets without distributions.
[datasets.values('source_url').filter(division_id=division_id).annotate(count=Count('distribution')).filter(count=0)[0].ckan_dataset_url for division_id in zero]

# Investigate datasets without distributions.
au = datasets.values('source_url').filter(division_id='ocd-division/country:au').annotate(count=Count('distribution'))
au.filter(count=0).count()
au.filter(count=0, description__icontains='[FOI Disclosure log here]').count()
au.filter(count=0).exclude(description__icontains='[FOI Disclosure log here]')

datasets.values('source_url').filter(division_id='ocd-division/country:br').annotate(count=Count('distribution')).filter(count=0)

nl = datasets.values('source_url', 'landingPage').filter(division_id='ocd-division/country:nl').annotate(count=Count('distribution'))
nl.filter(count=0).count()
nl.filter(count=0, landingPage__contains='nationaalgeoregister.nl/geonetwork').count()
nl.filter(count=0).exclude(landingPage__contains='nationaalgeoregister.nl/geonetwork')

datasets.values('source_url').filter(division_id='ocd-division/country:fi').annotate(count=Count('distribution')).filter(count=0)

datasets.values('source_url').filter(division_id='ocd-division/country:gb').annotate(count=Count('distribution')).filter(count=0)

datasets.values('source_url').filter(division_id='ocd-division/country:ie').annotate(count=Count('distribution')).filter(count=0)

datasets.values('source_url').filter(division_id='ocd-division/country:ph').annotate(count=Count('distribution')).filter(count=0)

datasets.values('source_url').filter(division_id='ocd-division/country:us').annotate(count=Count('distribution')).filter(count=0, landingPage='').exclude(extras_keys__contains=['landingPage'])
