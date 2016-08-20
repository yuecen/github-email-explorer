# -*- coding: utf-8 -*-

import argparse

import github_email
from email_handler import send_sendgrid_by_ges
from email_handler import send_sendgrid_by_email_list
from email_handler import get_email_template


class SendGridCliArgs(object):
    def __init__(self):
        p = argparse.ArgumentParser(prog='ge-sendgrid')
        p.add_argument('--api_key', help='Your KEY of SendGrid API')
        p.add_argument('--template_path', help='Your email template')
        p.add_argument('--action_type', default=['star'], nargs='+', help='"star", "fork" and "watch" are the only three options now')
        p.add_argument('--client_id', help='Github OAuth client ID')
        p.add_argument('--client_secret', help='Github OAuth client secret')

        args = p.parse_args()

        self.api_key = args.api_key
        self.action_type = args.action_type
        self.template_path = args.template_path
        self.client_id = args.client_id if args.client_id else ''
        self.client_secret = args.client_secret if args.client_secret else ''


def send_email_by_sendgrid():
    """
    Send email via SendGrid
    """
    sendgrid_cli_args = SendGridCliArgs()

    github_email_template = get_email_template(sendgrid_cli_args.template_path)
    metadata = github_email_template.metadata
    # List first
    if metadata['github_user']:
        print "Send email by list..."
        send_sendgrid_by_email_list(email_list=metadata['github_user'],
                                    sendgrid_api_key=sendgrid_cli_args.api_key,
                                    github_email_template=github_email_template)

    else:
        print "Send email by exploring..."
        # explore users email by action types
        github_api_auth = (sendgrid_cli_args.client_id, sendgrid_cli_args.client_secret)
        ges = github_email.collect_email_info(metadata['repository_owner'], metadata['repository_name'], sendgrid_cli_args.action_type, github_api_auth)
        print 'Total: {}/{}'.format(len([ge for ge in ges if ge.email]), len(ges))

        # send email by py-sendgrid
        send_sendgrid_by_ges(github_user_emails=ges,
                             sendgrid_api_key=sendgrid_cli_args.api_key,
                             github_email_template=github_email_template)


if __name__ == '__main__':
    send_email_by_sendgrid()
