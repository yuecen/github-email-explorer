from github_email_explorer import github_email

github_api_auth = ('<your_client_id>', '<your_client_secret>')
ges = github_email.collect_email_info(
    '<organization/user-id>', '<repo>', ['star', 'watch', 'fork'], github_api_auth=github_api_auth)

with open('data/output-watch.csv', 'wb') as file:
    for ge in ges:
        if ge.email:
            row = f"{ge.g_id},{ge.name},{ge.email},{ge.from_profile}".encode(
                "utf-8")
            file.write(row)
            file.write(b"\n")