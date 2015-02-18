import cgi
from optparse import make_option
from urllib.parse import quote

import requests
from requests_futures.sessions import FuturesSession

from . import InventoryCommand, number_to_human_size
from inventory.models import Distribution


class Command(InventoryCommand):
    args = '<identifier identifier ...>'
    help = 'Get HTTP headers for distributions'

    option_list = InventoryCommand.option_list + (
        make_option('--media-type', action='store', dest='media_type',
                    default='',
                    help='Get HTTP headers for this media type only.'),
    )

    def handle(self, *args, **options):
        self.setup(*args, **options)

        session = FuturesSession()

        # Collect the distribution-response pairs.
        def callback(distribution, response):
            results.append([distribution, response])

        # Create a closure.
        def factory(distribution):
            return lambda session, response: callback(distribution, response)

        for catalog in self.catalogs:
            distributions = Distribution.objects.filter(division_id=catalog.division_id, http_status_code__isnull=True)

            if options['media_type']:
                distributions = distributions.filter(mediaType=options['media_type'])

            if not distributions.exists():
                continue

            # @see https://djangosnippets.org/snippets/1949/
            pk = 0
            last_pk = distributions.order_by('-pk')[0].pk
            distributions = distributions.order_by('pk')
            while pk < last_pk:
                # @see https://github.com/ross/requests-futures/issues/18
                # @see https://github.com/ross/requests-futures/issues/5
                futures = []
                results = []

                for distribution in distributions.filter(pk__gt=pk)[:100]:
                    pk = distribution.pk

                    # @see http://docs.python-requests.org/en/latest/user/advanced/#body-content-workflow
                    # @see http://stackoverflow.com/a/845595/244258
                    futures.append(session.get(quote(distribution.accessURL, safe="%/:=&?~#+!$,;'@()*[]"),
                        stream=True,
                        allow_redirects=False,
                        background_callback=factory(distribution)))

                for future in futures:
                    try:
                        future.result()
                    except (requests.exceptions.InvalidSchema, requests.exceptions.InvalidURL, requests.exceptions.SSLError, requests.packages.urllib3.exceptions.ProtocolError):
                        self.exception('')

                for distribution, response in results:
                    status_code = response.status_code
                    charset = ''

                    content_length = response.headers.get('content-length')
                    if content_length:
                        content_length = int(content_length)

                    # @see https://github.com/kennethreitz/requests/blob/b137472936cbe6a6acabab538c1d05ed4c7da638/requests/utils.py#L308
                    content_type = response.headers.get('content-type', '')
                    if content_type:
                        content_type, params = cgi.parse_header(content_type)
                        if 'charset' in params:
                            charset = params['charset'].strip("'\"")

                    distribution.http_headers = dict(response.headers)
                    distribution.http_status_code = status_code
                    distribution.http_content_length = content_length
                    distribution.http_content_type = content_type
                    distribution.http_charset = charset
                    distribution.save()

                    self.debug('{} {} {}'.format(status_code, number_to_human_size(content_length), content_type))

                    response.close()
