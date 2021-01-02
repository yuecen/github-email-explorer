# -*- coding: utf-8 -*-

from collections import OrderedDict
import requests
from .api_url import GitHubEndPoint as EndPoint
import re
import math


class GithubUserEmail(object):
    def __init__(self, *args, **kwargs):
        self.g_id = None
        self.name = kwargs.get('name', None)
        self.email = kwargs.get('email', None)
        self.from_profile = kwargs.get('from_profile', None)
        if len(args) > 0 and (type(args[0]) is tuple):
            self.name = args[0][0]
            self.g_id = args[0][1]
            self.email = args[0][2]
            self.from_profile = args[0][3]


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
        total_pages = math.ceil(select_action_count(
            github_repo, action_type) / per_page)
        # create url
        url = EndPoint.add_auth_info(select_end_porint_builder(
            action_type)(user_id, repo), github_api_auth)
        # get id by rolling pages
        user_ids = user_ids + \
            request_user_ids_by_roll_pages(url, total_pages, per_page)

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
        user_ids = user_ids + \
            [info['login'] if 'login' in info else info['owner']['login']
                for info in r.json()]

    return user_ids


def collect_email_info(repo_user_id, repo_name, actions, github_api_auth=None):
    # get user ids
    user_ids = integrate_user_ids(
        repo_user_id, repo_name, actions, github_api_auth)
    # get and return email info
    return users_email_info(user_ids, github_api_auth)


def users_email_info(action_user_ids, github_api_auth):
    ges = []
    for user_id in action_user_ids:
        try:
            ges.append(request_user_email(user_id, github_api_auth))
        except requests.exceptions.HTTPError as e:
            print(e)
            # Return email addresses that have received after exception happened
            return ges

    return ges


def get_email_from_events(rsp, name):
    """
    Parses out the email, if available from a user's public events
    """
    rsp = rsp.json()
    for event in rsp:
        payload = event.get('payload')
        if payload is not None:
            commits = payload.get('commits')
            if commits is not None:
                for commit in commits:
                    author = commit.get('author')
                    if author['name'] == name:
                        return author.get('email')

    return None


def request_user_email(user_id, github_api_auth):
    """
    Get email from the profile
    """
    rsp = requests.get(EndPoint.add_auth_info(
        EndPoint.user_profile(user_id), github_api_auth))
    # raise error when found nothing
    rsp.raise_for_status()

    rsp = rsp.json()
    ge = GithubUserEmail()
    ge.g_id = rsp['login']
    ge.name = rsp['name'].strip() if rsp['name'] else rsp['login']
    ge.email = rsp['email']
    ge.from_profile = True

    # Get user email from events
    if ge.email is None:
        rsp = requests.get(EndPoint.add_auth_info(
            EndPoint.user_events(user_id), github_api_auth))
        # raise error when found nothing
        rsp.raise_for_status()

        email = get_email_from_events(rsp, ge.name)
        if email is not None:
            ge.email = email
            ge.from_profile = False

    # Check if user opted out and respect that
    if user_has_opted_out(ge.email):
        ge.email = None

    # Check if email can be used and not a noreply
    if email_is_github_noreply(ge.email):
        ge.email = None

    return ge


def user_has_opted_out(email):
    """
    Checks if an email address was marked as opt-out
    """
    if email is not None:
        regex = re.compile(
            '\\+[^@]*optout@g(?:oogle)?mail\\.com$', re.IGNORECASE)
        return regex.search(email) is not None
    else:
        return False


def email_is_github_noreply(email):
    """Checks if an email address is a github noreply e.g name@users.noreply.github.com
    Args:
        email (string): email address being checked
    """
    try:
        if email is not None:
            if email.split("@")[1] == "users.noreply.github.com":
                return True
        return False
    except Exception as ex:
        print(ex)
        return False


def format_email(ges):
    """
    John (john2) <John@example.org>; Peter James (pjames) <James@example.org>
    """
    formatted_email = []
    for ge in ges:
        if ge.email:
            try:
                formatted_email.append('{} ({}) <{}> [{}]'.format(
                    ge.name.encode('utf8'), ge.g_id, ge.email, ge.from_profile))
            except UnicodeEncodeError:
                print(f"{ge.g_id}, {ge.email}, {ge.from_profile}")
                continue

    formatted_email = '\n'.join(formatted_email)
    return formatted_email


def api_status(github_api_auth):
    rsp = requests.get(EndPoint.add_auth_info(
        EndPoint.rate_limit(), github_api_auth))
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
    rsp = requests.get(EndPoint.add_auth_info(
        EndPoint.repository(user_id, repo), github_api_auth))
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
    print('Total: {}/{}'.format(len([ge for ge in ges if ge.email]), len(ges)))
    print(format_email(ges))
