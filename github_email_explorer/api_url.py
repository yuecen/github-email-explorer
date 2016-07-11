# -*- coding: utf-8 -*-


class GitHubEndPoint(object):
    api_url = 'https://api.github.com/'

    @staticmethod
    def user_profile(user_id):
        return '{}users/{}'.format(GitHubEndPoint.api_url, user_id)

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
        return '{}?client_id={}&client_secret={}'.format(url, github_api_auth[0], github_api_auth[1])
