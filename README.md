## github-email-explorer

For people who want to create a email marketing plain for particular group on 
GitHub, github-email-explorer can send email to the group you want.

There are two main abilities, exploring email and sending email, into 
github-email-explorer that the concreted commends were named as ```ge-explore``` 
and ```ge-sendgrid```. SendGrid is only one email provider in current progress.

#### Installation

```bash
pip install github-email-explorer
```

#### Example of Getting Email List of Stargazers

The email list will be responded in a formatted string, which looks like,

```
John <John@example.org>; Peter James <James@example.org>;
```

You can copy list of address to any email service you have.  

```bash
$ ge-explore --repo <user_account>/<repo_name>

John <John@example.org>; Peter James <James@example.org>
```

If you encounter the situation of limitation from GitHub server during running 
the command, please add ```--client_id <your_github_auth_id> --client_secret <your_github_auth_secret>``` with the command above.

#### How to Send a Email to GitHub Users from a Particular Repository?

* Write Content using Template

You need to following syntax ```marketing_email.txt```

```
Hi {%email_to%},
We are currently in Product Hunt.
...
Thank you.
{%email_from%}
```

```{%email_to%}``` is a template syntax to 

#### Example of Getting API Status

In order to know API [rate limit] you are using, the status information can be 
found from github-email-explorer command.

Without authentication

```bash
$ ge-explore --status

Resource Type      Limit    Remaining  Reset Time
---------------  -------  -----------  --------------------
Core                  60           60  2016-07-07T04:56:12Z
Search                10           10  2016-07-07T03:57:12Z
```

With authentication

You can request more than 60 using authentication by [OAuth applications]

```bash
$ ge-explore --status --client_id <your_github_auth_id> --client_secret <your_github_auth_secret>

== GitHub API Status ==
Resource Type      Limit    Remaining  Reset Time
---------------  -------  -----------  --------------------
Core                5000         5000  2016-07-06T07:59:47Z
Search                30           30  2016-07-06T07:00:47Z
```

[rate limit]:https://developer.github.com/v3/rate_limit/
[OAuth applications]:https://github.com/settings/developers