# -*- coding: utf-8 -*-
import re
from setuptools import setup, find_packages

pkg_file = open("github_email_explorer/__init__.py").read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", pkg_file))
description = open('README.md').read()
requirements = [i.strip() for i in open("requirements.txt").readlines()]

setup(
    name='github-email-explorer',
    description='A tool to get email addresses from starred list of repositories on GitHub, and then send email to those addresses with template content.',
    version=metadata['version'],

    # Author details
    author='yuecen',
    author_email='yuecendev+pypi@gmail.com',
    url='https://github.com/yuecen/github-email-explorer',
    long_description=description,
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='github, email, sendgrid, marketing',
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ge-explore = github_email_explorer.cli_explore:get_github_email_by_repo',
            'ge-sendgrid = github_email_explorer.cli_sendgrid:send_email_by_sendgrid'
        ]
    }
)