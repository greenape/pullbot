from github3 import authorize
from getpass import getpass
import logging
import argparse

from pullbot.util import get_log_level

parser = argparse.ArgumentParser("pullbot-auth", description="A bot for automating GitHub Pull Requests.")
parser.add_argument("token_file", type=str, help="Path to a file containing a GitHub token.")
parser.add_argument("-v", "--verbosity", action="count", default=0)


def two_factor():
    code = ''
    while not code:
        # The user could accidentally press Enter before being ready,
        # let's protect them from doing that.
        code = input('Enter 2FA code: ')
    return code


def do_setup(token_file):
    logging.info("Beginning setup.\n")
    user = ''
    while not user:
        user = input('GitHub username: ')
    password = ''

    while not password:
        password = getpass('Password for {0}: '.format(user))

    note = 'PullBot'
    note_url = 'http://github.com/greenape/pullbot'
    scopes = ['user', 'repo']

    try:
        auth = authorize(user, password, scopes, note, note_url, two_factor_callback=two_factor)
        logging.info("Token acquired.\n")

        with open(token_file, 'w') as fd:
            fd.write("{}\n{}".format(auth.token, auth.id))
            logging.info("Wrote token to {}.\n".format(token_file))
    except Exception as e:
        logging.error("Auth failed: {}".format(e))


def main(args=None):
    args = parser.parse_args(args)
    logging.basicConfig(level=get_log_level(args.verbosity), format='%(asctime)s %(name)s %(levelname)s %(message)s')
    do_setup(args.token_file)
