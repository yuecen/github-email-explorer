# -*- coding: utf-8 -*-

from collections import OrderedDict
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


class GithubRepository(object):
    def __init__(self):
        self.repo_id = None
        self.name = None
        self.description = None
        self.stargazers_count = 0
        self.watchers_count = 0
        self.forks_count = 0


def select_end_porint_builder(act_type):
    return {
        'star': EndPoint.stargazers,
        'fork': EndPoint.forks,
        'watch': EndPoint.watchers,
    }[act_type]


def select_action_count(github_repo, action_type):
    if action_type == 'star':
        return github_repo.stargazers_count
    if action_type == 'fork':
        return github_repo.forks_count
    if action_type == 'watch':
        return github_repo.watchers_count


def integrate_user_ids(user_id, repo, actions, github_api_auth):
    user_ids = []
    for action_type in actions:
        # get repo
        github_repo = repository(user_id, repo, github_api_auth)
        # pagination
        per_page = 100
        total_pages = select_action_count(github_repo, action_type) / per_page
        # create url
        url = EndPoint.add_auth_info(select_end_porint_builder(action_type)(user_id, repo), github_api_auth)
        # get id by rolling pages
        user_ids = user_ids + request_user_ids_by_roll_pages(url, total_pages, per_page)

    return OrderedDict.fromkeys(user_ids).keys()


def request_user_ids_by_roll_pages(url, total_pages, per_page):
    # loop page with url
    user_ids = []
    for i in range(0, total_pages + 1):
        url = EndPoint.pagination(url, page=(i + 1), per_page=per_page)
        r = requests.get(url)

        # raise error when found nothing
        r.raise_for_status()

        # handling result
        user_ids = user_ids + [info['login'] if 'login' in info else info['owner']['login'] for info in r.json()]

    return user_ids


def collect_email_info(repo_user_id, repo_name, actions, github_api_auth=None):
    # get user ids
    user_ids = integrate_user_ids(repo_user_id, repo_name, actions, github_api_auth)
    # get and return email info
    return users_email_info(user_ids, github_api_auth)


def users_email_info(action_user_ids, github_api_auth):
    ges = []
    for user_id in action_user_ids:
        try:
            ges.append(request_user_email(user_id, github_api_auth))
        except requests.exceptions.HTTPError as e:
            print e
            # Return email addresses that have received after exception happened
            return ges

    return ges


def request_user_email(user_id, github_api_auth):
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


def repository(user_id, repo, github_api_auth):
    rsp = requests.get(EndPoint.add_auth_info(EndPoint.repository(user_id, repo), github_api_auth))
    rsp = rsp.json()
    repo = GithubRepository()
    repo.repo_id = rsp['id']
    repo.name = rsp['name']
    repo.description = rsp['description']
    repo.stargazers_count = rsp['stargazers_count']
    repo.watchers_count = rsp['watchers_count']
    repo.forks_count = rsp['forks_count']
    return repo


if __name__ == '__main__':
    # print request_user_email('yuecen')
    ges = collect_email_info('yuecen', 'github-email-explorer', ['star'])
    print 'Total: {}/{}'.format(len([ge for ge in ges if ge.email]), len(ges))
    print format_email(ges)
