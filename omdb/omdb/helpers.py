import re
import requests


class OmdbMixin(object):
    def _build_url(self, params):
        schema = u'http://'
        netloc = u'www.omdbapi.com'
        api_key = u'aca22ed8'
        path = u'/?apikey={api_key}'.format(api_key=api_key)
        url = u'{schema}{netloc}{path}&{params}'.format(
            schema=schema,
            netloc=netloc,
            path=path,
            params=u'&'.join([u'%s=%s' % item for item in params.items()])
        )
        return url

    def build_url(self, title_or_id):
        # identify if it's an movie_id eg. tt1234567
        if re.match(r'^tt\d{7}$', title_or_id):
            return self._build_url({'i': title_or_id})
        return self._build_url({'s': title_or_id})

    def get_page_data(self, title_or_id):
        return requests.get(
            self.build_url(title_or_id)
        ).json()
