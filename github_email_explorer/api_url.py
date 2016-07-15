# -*- coding: utf-8 -*-
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit


class GitHubEndPoint(object):
    api_url = 'https://api.github.com/'

    @staticmethod
    def user_profile(user_id):
        return '{}users/{}'.format(GitHubEndPoint.api_url, user_id)

    @staticmethod
    def repository(user_id, repo):
        return '{}repos/{}/{}'.format(GitHubEndPoint.api_url, user_id, repo)

    @staticmethod
    def stargazers(user_id, repo):
        return '{}repos/{}/{}/stargazers'.format(GitHubEndPoint.api_url, user_id, repo)

    @staticmethod
    def rate_limit():
        return '{}rate_limit'.format(GitHubEndPoint.api_url)

    @staticmethod
    def add_auth_info(url, github_api_auth):
        if github_api_auth is None:
            github_api_auth = ('', '')
        url = set_url_parameter(url, 'client_id', github_api_auth[0])
        url = set_url_parameter(url, 'client_secret', github_api_auth[1])
        return url

    @staticmethod
    def pagination(url, page=1, per_page=100):
        url = set_url_parameter(url, 'page', page)
        url = set_url_parameter(url, 'per_page', per_page)
        return url


def set_url_parameter(url, param_name, param_value):
    """Set or replace a query parameter and return the modified URL.

    >>> set_url_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'

    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))