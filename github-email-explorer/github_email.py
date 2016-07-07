# -*- coding: utf-8 -*-

import requests
import api_url


class GithubUserEmail(object):
    def __init__(self):
        self.g_id = None
        self.name = None
        self.email = []


class GithubAPIStatus(object):
    def __init__(self):
        self.core_limit = None
        self.core_remaining = None
        self.core_reset_time = None
        self.search_limit = None
        self.search_remaining = None
        self.search_reset_time = None


def stargazers_user_ids(user_id, repo):
    r = requests.get(api_url.stargazers(user_id, repo))
    return [info['login'] for info in r.json()]


def user_emails(user_id):
    """
    Get email from the profile
    """

    rsp = requests.get(api_url.user_profile(user_id))
    rsp = rsp.json()
    ge = GithubUserEmail()
    ge.g_id = rsp['login']
    ge.name = rsp['name'] if rsp['name'] else rsp['login']
    ge.name = ge.name.encode('utf-8')
    ge.email = rsp['email']

    # TODO user email from the event

    return ge


def stargazers_emails(repo_user_id, repo_name):
    stargazers_ids = stargazers_user_ids(repo_user_id, repo_name)
    return [user_emails(user_id) for user_id in stargazers_ids]


def format_email(ges):
    """
    John <John@example.org>; Peter James <James@example.org>
    """

    formatted_email = ['{} <{}>'.format(ge.name, ge.email) for ge in ges if ge.email]
    formatted_email = '; '.join(formatted_email)
    return formatted_email


def api_status():
    rsp = requests.get(api_url.rate_limit())
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

