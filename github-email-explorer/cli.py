# -*- coding: utf-8 -*-

from datetime import datetime
from tabulate import tabulate
import argparse
import re
import github_email


class ExploreCliArgs:
    def __init__(self):
        p = argparse.ArgumentParser(prog='ge-explore')
        p.add_argument('--repo', help='Repo on Github, type "<account>/<repo>"')
        p.add_argument('--action_type', default='starred', help='"starred" is the only option now')
        p.add_argument('--client_id', help='Github OAuth client ID')
        p.add_argument('--client_secret', help='Github OAuth client secret')
        p.add_argument('--status', action='store_true', help='Github API status')

        args = p.parse_args()

        self.repo = args.repo
        self.repo_user = None
        self.repo_name = None
        if self.repo:
            tmp = re.split('/', self.repo)
            assert len(tmp) == 2, "repo format is not correct"

            self.repo_user, self.repo_name = tmp[0], tmp[1]

        self.action_type = args.action_type
        self.client_id = args.client_id if args.client_id else ''
        self.client_secret = args.client_secret if args.client_secret else ''
        self.status = args.status


class SendGridCliArgs:
    def __init__(self):
        p = argparse.ArgumentParser(prog='ge-sendgrid')
        p.add_argument('--api_user', help='Your user name of SendGrid API')
        p.add_argument('--api_key', help='Your user key of SendGrid API')
        p.add_argument('--email', required=True, nargs='+', help='Email address')

        args = p.parse_args()

        self.api_user = args.api_user
        self.api_key = args.api_key
        self.email_file = args.email_file


def get_github_email_by_repo():
    """ Get user email by repos
    """
    explore_cli_args = ExploreCliArgs()
    if explore_cli_args.status:
        # call api status
        status = github_email.api_status()
        table = [["Core", status.core_limit, status.core_remaining, datetime.utcfromtimestamp(status.core_reset_time).strftime('%Y-%m-%dT%H:%M:%SZ')],
                 ["Search", status.search_limit, status.search_remaining, datetime.utcfromtimestamp(status.search_reset_time).strftime('%Y-%m-%dT%H:%M:%SZ')]]
        print "== GitHub API Status =="
        print tabulate(table, headers=['Resource Type', 'Limit', 'Remaining', 'Reset Time'])
        return

    # get repo from explore_cli_args
    if explore_cli_args.action_type == 'starred':
        ges = github_email.stargazers_emails(explore_cli_args.repo_user, explore_cli_args.repo_name)
    print github_email.format_email(ges)


def send_email_by_sendgrid():
    """
    Send email via SendGrid
    """
    sendgrid_cli_args = SendGridCliArgs()
    # read email content from file

    # send email by py-sendgrid

if __name__ == '__main__':
    get_github_email_by_repo()
