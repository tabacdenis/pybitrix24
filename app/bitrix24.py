import json
import requests
import urllib.parse


class Bitrix24(object):
    _oauth_path_template = 'https://{domain}/oauth/{action}/'

    def __init__(self, domain, client_id, client_secret, access_token=None,
                 client_endpoint=None, expires_in=3600, refresh_token=None,
                 scope=None, server_endpoint=None, user_id=None):
        self.access_token = access_token
        self.client_id = client_id
        self.client_endpoint = client_endpoint
        self.client_secret = client_secret
        self.domain = domain
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.scope = scope
        self.server_endpoint = server_endpoint
        self.user_id = user_id

    def _get_oauth_endpoint(self, action, query=None):
        """
        Build an OAuth URL with/out query parameters.
        :param action: str Action name of an OAuth endpoint
        :param query: dict Query parameters
        :return: str OAuth endpoint
        """
        endpoint = self._oauth_path_template.format(
            domain=self.domain,
            action=action
        )
        if query is not None:
            query = urllib.parse.urlencode(query)
            endpoint = '{}?{}'.format(endpoint, query)
        return endpoint

    def get_authorize_endpoint(self, **extra_query):
        """
        Build an authorize URL to request an authorization code from
        a remote server using a browser.
        :param extra_query: dict Additional query parameters
        :return: str Authorize endpoint
        """
        query = extra_query.copy()
        query.update({
            'client_id': self.client_id,
            'response_type': 'code'
        })
        return self._get_oauth_endpoint('authorize', query)

    def get_tokens(self):
        """
        Return current access and refresh tokens of the instance.
        :return: dict Access and refresh tokens
        """
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        }

    def _request_tokens(self, query):
        """
        Request handler of an OAuth tokens endpoint.
        :param query: dict Query parameters
        :return: dict Encoded response text
        """
        url = self._get_oauth_endpoint('token')
        r = requests.get(url, params=query)
        result = json.loads(r.text)
        return result

    def request_tokens(self, code, **extra_query):
        """
        Request access and refresh tokens of a Bitrix24 server.
        :param code: str Authentication request code
        :param extra_query: dict Additional query parameters
        """
        query = extra_query.copy()
        query.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        })
        result = self._request_tokens(query)
        self.access_token = result.get('access_token')
        self.client_endpoint = result.get('client_endpoint')
        self.domain = result.get('domain')
        self.expires_in = result.get('expires_in')
        self.refresh_token = result.get('refresh_token')
        self.scope = result.get('scope')
        self.server_endpoint = result.get('server_endpoint')
        self.user_id = result.get('user_id')

    def refresh_tokens(self, **extra_query):
        """
        Refresh class tokens by appropriate requested tokens.
        :param extra_query: dict Additional query parameters
        """
        query = extra_query.copy()
        query.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        })
        result = self._request_tokens(query)
        self.access_token = result.get('access_token')
        self.refresh_token = result.get('refresh_token')

    def call_method(self, name):
        pass