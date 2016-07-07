# -*- coding: utf-8 -*-
from cli import ExploreCliArgs

api_url = 'https://api.github.com/'

explore_cli_args = ExploreCliArgs()

def user_profile(user_id):
    return add_auth_info('{}users/{}'.format(api_url, user_id))


def stargazers(user_id, repo):
    return add_auth_info('{}repos/{}/{}/stargazers'.format(api_url, user_id, repo))


def rate_limit():
    return add_auth_info('{}rate_limit'.format(api_url))


def add_auth_info(url):
    return '{}?client_id={}&client_secret={}'.format(url, explore_cli_args.client_id, explore_cli_args.client_secret)