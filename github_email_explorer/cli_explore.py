# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import datetime
from tabulate import tabulate
import argparse
import re

from . import github_email


def record_args(name, d):
    return namedtuple(name, d.keys())(**d)


class ExploreCliArgs(object):
    def __init__(self):
        p = argparse.ArgumentParser(prog='ge-explore')
        p.add_argument('--repo', help='Repo on Github, type "<owner>/<repo>"')
        p.add_argument('--action_type', default=['star'], nargs='+', help='"star", "fork" and "watch" are the only three options now')
        p.add_argument('--client_id', help='Github OAuth client ID')
        p.add_argument('--client_secret', help='Github OAuth client secret')
        p.add_argument('--status', action='store_true', help='Github API status')

        args = p.parse_args()

        self.repo = args.repo
        if self.repo:
            tmp = re.split('/', self.repo)
            assert len(tmp) == 2, "repo format is not correct"

            self.repo = record_args('repo', {'owner': tmp[0], 'name': tmp[1]})

        self.action_type = args.action_type
        self.client_id = args.client_id if args.client_id else ''
        self.client_secret = args.client_secret if args.client_secret else ''
        self.status = args.status


def get_github_email_by_repo():
    """ Get user email by repos
    """
    explore_cli_args = ExploreCliArgs()

    github_api_auth = (explore_cli_args.client_id, explore_cli_args.client_secret)

    if explore_cli_args.status:
        # call api status
        status = github_email.api_status(github_api_auth)
        table = [["Core", status.core_limit, status.core_remaining, datetime.utcfromtimestamp(status.core_reset_time).strftime('%Y-%m-%dT%H:%M:%SZ')],
                 ["Search", status.search_limit, status.search_remaining, datetime.utcfromtimestamp(status.search_reset_time).strftime('%Y-%m-%dT%H:%M:%SZ')]]
        print("== GitHub API Status ==")
        print (tabulate(table, headers=['Resource Type', 'Limit', 'Remaining', 'Reset Time']))
        return

    # handle action_type
    ges = github_email.collect_email_info(explore_cli_args.repo.owner, explore_cli_args.repo.name, explore_cli_args.action_type, github_api_auth)
    print ('Total: {}/{}'.format(len([ge for ge in ges if ge.email]), len(ges)))
    print (github_email.format_email(ges))


if __name__ == '__main__':
    get_github_email_by_repo()
