from itertools import cycle
from time import sleep

from github3 import authorize, login
from getpass import getpass
import logging
logging.basicConfig(level=logging.INFO)


def two_factor():
    code = ''
    while not code:
        # The user could accidentally press Enter before being ready,
        # let's protect them from doing that.
        code = input('Enter 2FA code: ')
    return code


def do_setup():
    logging.info("Beginning setup.\n")
    user = ''
    while not user:
        user = input('GitHub username: ')
    password = ''

    while not password:
        password = getpass('Password for {0}: '.format(user))

    note = 'Flowminder autoassigner'
    note_url = 'http://flowminder.org'
    scopes = ['user', 'repo']

    auth = authorize(user, password, scopes, note, note_url, two_factor_callback=two_factor)

    with open("./token", 'w') as fd:
        fd.write("{}\n{}".format(auth.token, auth.id))
        logging.info("Token acquired.\n")
    users = input("Enter assignees separated by spaces: ").split(' ')
    with open("./user_rota", "w") as fout:
        for user in users:
            fout.write("{}\n".format(user))
    repos = input("Enter repos to watch separated by spaces (e.g. Flowminder/nerve): ").split(' ')
    with open("./repos", "w") as fout:
        for repo in repos:
            fout.write("{}\n".format(repo))


def first_not(rota, user):
    """
    Return the first entry of rota not equal to user.
    :param rota:
    :param user:
    :return:
    """
    for rotad in rota:
        if rotad != user:
            return rotad


if __name__ == "__main__":
    try:
        logging.info("Starting assignerbot.")
        token = id = ''
        logging.info("Authenticating.")
        with open("/gh_cred", 'r') as fd:
            token = fd.readline().strip()  # Can't hurt to be paranoid
            id = fd.readline().strip()
        gh = login(id, token)
        logging.info("Loading user rota.")
        with open("/user_rota", "r") as fin:
            users = [x.strip() for x in fin.readlines()]
        user_rota = cycle(users)

        logging.info("Loading repos.")
        with open("/repos", "r") as fin:
            repo_names = fin.readlines()
            repos = [gh.repository(*repo.strip().split("/")) for repo in repo_names]
            logging.info("Watching {}".format(repos))
        while True:
            try:
                for repo in repos:
                    prs = [x.issue() for x in repo.pull_requests(state="open") if x.assignee is None]
                    logging.info("Got {} unassigned open issues for {}".format(len(prs), repo))
                    for pr in prs:
                        pr_owner = pr.user.login
                        next_assignee = first_not(user_rota, pr_owner)
                        logging.info("Assigning {} #{} to {}".format(repo, pr.number, next_assignee))
                        pr.assign(next_assignee)
                        logging.info("Assigned {} #{} to {}".format(repo.name, pr.number, next_assignee))
            except Exception as e:
                logging.error("Error talking to github, waiting a bit. Error was {}".format(e))
            logging.info("Sleeping for 10 mins.")
            sleep(600)
    except Exception as e:
        logging.debug(e)
        do_setup()

