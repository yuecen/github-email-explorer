# -*- coding: utf-8 -*-

from jinja2 import FileSystemLoader
from jinja2 import Environment

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail

import sys


template_loader = FileSystemLoader(searchpath="/")
template_env = Environment(loader=template_loader)


class EmailContent(object):
    def __init__(self):
        self.email_from = None
        self.email_to = None
        self.email_content = None
        self.provider = None


def parse_email():
    pass


def send_sendgrid_by_email_list(email_list):
    pass


def send_sendgrid_by_ges(sendgrid_api_key=None, email_template=None, github_user_emails=None, from_email=None, subject=None):

    assert sendgrid_api_key, "SendGrid API key is required"

    sg = SendGridAPIClient(apikey=sendgrid_api_key)
    from_email = Email(from_email)
    subject = subject
    for ge in github_user_emails:
        to_email = Email(ge.email)
        content = Content("text/html", email_template.render(to_name=ge.name))
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())

        if response.status_code > 300:
            # More than 300 means something wrong, do nothing.
            sys.exit()


def get_email_template(path):
    return template_env.get_template(path)


if __name__ == '__main__':
    pass
