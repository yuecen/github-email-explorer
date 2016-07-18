from github_email_explorer import github_email

# github_api_auth = ('<your_client_id>', '<your_client_secret>')
# ges = github_email.collect_email_info('yuecen', 'github-email-explorer', ['star'], github_api_auth=github_api_auth)

ges = github_email.collect_email_info('yuecen', 'github-email-explorer', ['star'])

for ge in ges:
    print ge.name, "->", ge.email
