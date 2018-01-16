# pullbot

pullbot is a simple bot for automating some tedious bits of GitHub pull requests.

pullbot automatically assigns reviewers based on a rota system.

Use pullbot like this:

```bash
pullbot-auth my_github_token_file
```

To generate a personal access token with user and repo access.

Then do this:

```bash
pullbot my_github_token_file --repos username/reponame username/another_reponame --users octocat greenape
```

To set pullbot watching your repos. The next time a pull request is issued, pullbot will assign it to octocat. Then, the one after that will be assigned to @greenape (and so on).

If the pull request was initiated by the next user in the rota, they'll get skipped, and will be first in line for the next one.
