# -*- coding: utf-8 -*-

import argparse
import re

import github_email
from email_handler import send_sendgrid_by_ges
from email_handler import send_sendgrid_by_email_list
from email_handler import get_email_template


class SendGridCliArgs(object):
    def __init__(self):
        p = argparse.ArgumentParser(prog='ge-sendgrid')
        p.add_argument('--api_key', help='Your KEY of SendGrid API')
        p.add_argument('--template_path', help='Your email template')
        p.add_argument('--subject', required=True, help='Subject of email')
        p.add_argument('--from_email', required=True, help='Address form')
        p.add_argument('--explore_starred', help='Explore a repo people have starred')
        p.add_argument('--client_id', help='Github OAuth client ID')
        p.add_argument('--client_secret', help='Github OAuth client secret')
        p.add_argument('--list', help='Email list')

        args = p.parse_args()

        self.api_key = args.api_key

        self.explore_starred = args.explore_starred
        if self.explore_starred:
            tmp = re.split('/', self.explore_starred)
            assert len(tmp) == 2, "repo format is not correct"

            self.repo_user, self.repo_name = tmp[0], tmp[1]

        self.list = args.list
        if (self.list is not None) and (self.explore_starred is not None):
            raise ValueError("list and explore_starred is exclusive")

        self.template_path = args.template_path
        self.subject = args.subject
        self.from_email = args.from_email
        self.client_id = args.client_id if args.client_id else ''
        self.client_secret = args.client_secret if args.client_secret else ''


def send_email_by_sendgrid():
    """
    Send email via SendGrid
    """
    sendgrid_cli_args = SendGridCliArgs()

    if sendgrid_cli_args.explore_starred:

        # explore starred users email
        github_api_auth = (sendgrid_cli_args.client_id, sendgrid_cli_args.client_secret)
        ges = github_email.stargazers_email_info(sendgrid_cli_args.repo_user, sendgrid_cli_args.repo_name, github_api_auth)
        # print github_email.format_email(ges)

        # read email content from file
        email_template = get_email_template(sendgrid_cli_args.template_path)

        # send email by py-sendgrid
        send_sendgrid_by_ges(github_user_emails=ges,
                             sendgrid_api_key=sendgrid_cli_args.api_key,
                             email_template=email_template, from_email=sendgrid_cli_args.from_email,
                             subject=sendgrid_cli_args.subject)

    if sendgrid_cli_args.list:
        email_template = get_email_template(sendgrid_cli_args.template_path)
        send_sendgrid_by_email_list(email_list=sendgrid_cli_args.list,
                                    sendgrid_api_key=sendgrid_cli_args.api_key,
                                    email_template=email_template, from_email=sendgrid_cli_args.from_email,
                                    subject=sendgrid_cli_args.subject)


if __name__ == '__main__':
    send_email_by_sendgrid()
