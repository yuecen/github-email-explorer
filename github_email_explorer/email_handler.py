# -*- coding: utf-8 -*-
from github_email import GithubUserEmail

from jinja2 import FileSystemLoader
from jinja2 import Environment

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail

import re
import sys


template_loader = FileSystemLoader(searchpath="/")
template_env = Environment(loader=template_loader)


class EmailContent(object):
    def __init__(self):
        self.email_from = None
        self.email_to = None
        self.email_content = None
        self.provider = None


def parse_email(address):
    r = re.match('(?P<name>.*)\s*\((?P<g_id>.*)\)\s<(?P<email>.*?)>', address)
    e = r.groupdict()
    name, g_id, email = e['name'], e['g_id'], e['email']
    return name.decode('utf8'), g_id, email


def send_sendgrid_by_email_list(email_list=None, sendgrid_api_key=None, email_template=None, from_email=None, subject=None):
    email_list = re.split(';', email_list)
    github_user_emails = [GithubUserEmail(parse_email(address)) for address in email_list if len(address.strip()) > 0]

    send_sendgrid(github_user_emails=github_user_emails, sendgrid_api_key=sendgrid_api_key,
                  email_template=email_template, from_email=from_email, subject=subject)


def send_sendgrid_by_ges(github_user_emails=None, sendgrid_api_key=None, email_template=None, from_email=None, subject=None):
    github_user_emails = [ge for ge in github_user_emails if ge.email]

    send_sendgrid(github_user_emails=github_user_emails, sendgrid_api_key=sendgrid_api_key,
                  email_template=email_template, from_email=from_email, subject=subject)


def send_sendgrid(sendgrid_api_key=None, email_template=None, github_user_emails=None, from_email=None, subject=None):

    assert sendgrid_api_key, "SendGrid API key is required"

    sg = SendGridAPIClient(apikey=sendgrid_api_key)

    from_email = Email(from_email)
    for ge in github_user_emails:
        to_email = Email(ge.email)
        content = Content("text/html", email_template.render(github_user=ge))
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())

        if response.status_code > 300:
            # More than 300 means something wrong, do nothing.
            sys.exit()


def get_email_template(path):
    return GitHubEmailTemplate(path)


class GitHubEmailTemplate(object):
    def __init__(self, template_path):
        self.template_path = template_path
        self._email_template = template_env.get_template(template_path)

        self.repo = None

    def render(self, **kwargs):
        return self._email_template.render(kwargs, repo=self.repo)


if __name__ == '__main__':
    # send_sendgrid_by_email_list(' <John@example.org>; Peter James <James@example.org>;')

    def record_args(name, d):
        from collections import namedtuple
        return namedtuple(name, d.keys())(**d)

    gt = GitHubEmailTemplate('../examples/marketing_email.txt')
    gt.repo = record_args('repo', {'owner': 'yuecen', 'name': 'github-email-explorer'})
    ge = GithubUserEmail(('test', 'test@example.com'))
    print gt.render(github_user=ge)
