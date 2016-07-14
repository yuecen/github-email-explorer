# -*- coding: utf-8 -*-

import requests
from api_url import GitHubEndPoint as EndPoint


class GithubUserEmail(object):
    def __init__(self, *args, **kwargs):
        self.g_id = None
        self.name = kwargs.get('name', None)
        self.email = kwargs.get('email', None)
        if len(args) > 0 and (type(args[0]) is tuple):
            self.name = args[0][0]
            self.email = args[0][1]


class GithubAPIStatus(object):
    def __init__(self):
        self.core_limit = None
        self.core_remaining = None
        self.core_reset_time = None
        self.search_limit = None
        self.search_remaining = None
        self.search_reset_time = None


def stargazers_user_ids(user_id, repo, github_api_auth):
    r = requests.get(EndPoint.add_auth_info(EndPoint.stargazers(user_id, repo), github_api_auth))

    # raise error when found nothing
    r.raise_for_status()

    return [info['login'] for info in r.json()]


def user_emails(user_id, github_api_auth):
    """
    Get email from the profile
    """

    rsp = requests.get(EndPoint.add_auth_info(EndPoint.user_profile(user_id), github_api_auth))
    # raise error when found nothing
    rsp.raise_for_status()

    rsp = rsp.json()
    ge = GithubUserEmail()
    ge.g_id = rsp['login']
    ge.name = rsp['name'] if rsp['name'] else rsp['login']
    ge.name = ge.name.encode('utf-8')
    ge.email = rsp['email']

    # TODO user email from events

    return ge


def stargazers_emails(repo_user_id, repo_name, github_api_auth=None):
    stargazers_ids = stargazers_user_ids(repo_user_id, repo_name, github_api_auth)
    ges = []
    for user_id in stargazers_ids:
        try:
            ges.append(user_emails(user_id, github_api_auth))
        except requests.exceptions.HTTPError as e:
            print e
            # Return email addresses that have received after exception happened
            return ges

    return ges


def format_email(ges):
    """
    John <John@example.org>; Peter James <James@example.org>
    """

    formatted_email = ['{} <{}>'.format(ge.name, ge.email) for ge in ges if ge.email]
    formatted_email = '; '.join(formatted_email)
    return formatted_email


def api_status(github_api_auth):
    rsp = requests.get(EndPoint.add_auth_info(EndPoint.rate_limit(), github_api_auth))
    rsp = rsp.json()
    status = GithubAPIStatus()
    status.core_reset_time = rsp['resources']['core']['reset']
    status.core_limit = rsp['resources']['core']['limit']
    status.core_remaining = rsp['resources']['core']['remaining']
    status.search_reset_time = rsp['resources']['search']['reset']
    status.search_limit = rsp['resources']['search']['limit']
    status.search_remaining = rsp['resources']['search']['remaining']
    return status


if __name__ == '__main__':
    print user_emails('yuecen')
    ges = stargazers_emails('yuecen', 'elk-conf')
    print format_email(ges)

