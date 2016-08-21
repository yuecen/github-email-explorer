# -*- coding: utf-8 -*-
from github_email import GithubUserEmail

from jinja2 import FileSystemLoader
from jinja2 import Environment

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail

import codecs
import re
import sys


template_loader = FileSystemLoader(searchpath="/")
template_env = Environment(loader=template_loader)

ESSENTIAL_FIELDS = ['subject', 'from', 'github_user',
                    'repository', 'repository_owner', 'repository_name']


def parse_email(address):
    r = re.match('(?P<name>.*)\s*\((?P<g_id>.*)\)\s<(?P<email>.*?)>', address)
    e = r.groupdict()
    name, g_id, email = e['name'], e['g_id'], e['email']
    return name.decode('utf8'), g_id, email


def parse_into_github_user_emails(email_list):
    email_list = re.split(';', email_list)
    github_user_emails = [GithubUserEmail(parse_email(address)) for address in email_list if len(address.strip()) > 0]
    return github_user_emails


def send_sendgrid_by_ges(github_user_emails=None, sendgrid_api_key=None, github_email_template=None):
    github_user_emails = [ge for ge in github_user_emails if ge.email]

    send_sendgrid(github_user_emails=github_user_emails, sendgrid_api_key=sendgrid_api_key,
                  github_email_template=github_email_template)


def send_sendgrid(sendgrid_api_key=None, github_email_template=None, github_user_emails=None):

    assert sendgrid_api_key, "SendGrid API key is required"

    sg = SendGridAPIClient(apikey=sendgrid_api_key)

    metadata = github_email_template.metadata

    from_email = Email(metadata['from'])
    for ge in github_user_emails:

        # Add github_user into metadata
        metadata['github_user'] = ge

        # Render content with metadata
        content = Content("text/html", github_email_template.render_content(metadata))

        # Render subject with metadata
        subject = template_env.from_string(metadata['subject']).render(metadata)

        to_email = Email(ge.email)
        mail = Mail(from_email, subject, to_email, content)
        _body = mail.get()

        # Add custom args for log fields
        _custon = {}
        for key, value in metadata.iteritems():
            if key not in ESSENTIAL_FIELDS:
                _custon[key] = value
        _custon['repository'] = metadata['repository']
        _body['custom_args'] = _custon

        response = sg.client.mail.send.post(request_body=_body)

        if response.status_code > 300:
            # More than 300 means something wrong, do nothing.
            sys.exit()


def get_email_template(path):
    github_email_template = GitHubEmailTemplate()
    github_email_template.set_material(path)
    return github_email_template


class BaseReader(object):
    def __init__(self, *args, **kwargs):
        pass

    def read(self, source_path):
        """Return metadata and template"""
        material = material_open(source_path)
        res = re.match(r'(?P<metadata>[\s\S]*?)\n\n(?P<template>[\s\S]*)', material).groupdict()
        return self._parse_metadata(res['metadata']), res['template']

    def _parse_metadata(self, meta):
        # add essential fields
        format_meta = {ess_field: '' for ess_field in ESSENTIAL_FIELDS}
        res = re.findall(r'([\s\S]*?):([\s\S]*?)(\n|$)', meta)
        for r in res:
            format_meta[r[0].strip()] = r[1].strip()

        return format_meta


class GitHubEmailTemplate(BaseReader):
    def __init__(self, *args, **kwargs):
        super(GitHubEmailTemplate, self).__init__(*args, **kwargs)
        self._email_template = None
        self.metadata = {}

    def set_material(self, source_path):
        self.metadata, template = self.read(source_path)
        self._email_template = template_env.from_string(template)

    def render_content(self, meta):
        """Render email content with a template."""
        if meta:
            return self._email_template.render(meta)
        else:
            return self._email_template.render(self.metadata)


def material_open(filename, mode='rb', strip_crs=(sys.platform == 'win32')):
    with codecs.open(filename, mode, encoding='utf-8') as infile:
        content = infile.read()
    if content[0] == codecs.BOM_UTF8.decode('utf8'):
        content = content[1:]
    if strip_crs:
        content = content.replace('\r\n', '\n')
    return content


if __name__ == '__main__':
    # send_sendgrid_by_email_list(' <John@example.org>; Peter James <James@example.org>;')

    gt = GitHubEmailTemplate('../examples/marketing_email.txt')
    print gt.render()
