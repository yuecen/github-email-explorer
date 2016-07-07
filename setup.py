# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

description = open('README.md').read()
requirements = [i.strip() for i in open("requirements.txt").readlines()]

setup(
    name='github-email-explorer',
    description='A tool to send a content to ',
    version='0.0.1',

    # Author details
    author='yuecen',
    author_email='yuecendev+pypi@gmail.com',
    url='https://github.com/yuecen/github-email-explorer',
    long_description=description,
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
    keywords='github, email, sendgrid, marketing',
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ge-explore = github-email-explorer.cli:get_github_email_by_repo',
            'ge-sendgrid = github-email-explorer.cli:send_email_by_sendgrid'
        ]
    }
)