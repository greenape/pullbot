from itertools import cycle, count, chain
from time import sleep
import argparse
from github3 import login
import logging

from pullbot.util import get_log_level
from pullbot import __version__

parser = argparse.ArgumentParser("PullBot", description="A bot for automating GitHub Pull Requests.")
parser.add_argument("token_file", type=str, help="Path to a file containing a GitHub token.")
parser.add_argument("-r", "--repos", type=str, nargs="+", help="Repositories to watch")
parser.add_argument("-u", "--users", type=str, nargs="+", help="Users to rota.")
parser.add_argument("-v", "--verbosity", action="count", default=0)
parser.add_argument("-i", "--poll-interval", type=int, help="Seconds to wait between checks.", default=600)
parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))


def first_not(rota, user):
    """
    Return the first entry of rota not equal to user.
    :param rota: generator
    :param user: str
    :return: first value of rota != user, and rota with user prepended if they were originally next
    """
    modified_rota = rota
    for rotad in rota:
        if rotad != user:
            return rotad, modified_rota
        modified_rota = chain([user], rota)


def main(looper=count(), args=None):
    parser.add_help = True
    args = parser.parse_args(args)
    logging.basicConfig(level=get_log_level(args.verbosity), format='%(asctime)s %(name)s %(levelname)s %(message)s')
    try:
        logging.info("Starting assignerbot.")
        token = id = ''
        logging.info("Authenticating.")
        with open(args.token_file, 'r') as fd:
            token = fd.readline().strip()
            id = fd.readline().strip()
        gh = login(id, token)
        logging.info("Loading user rota.")
        user_rota = cycle(args.users)

        logging.info("Loading repos.")
        repos = [gh.repository(*repo.strip().split("/")) for repo in args.repos]
        logging.info("Watching {}".format(repos))
        for i in looper:
            try:
                for repo in repos:
                    prs = [x.issue() for x in repo.pull_requests(state="open") if x.assignee is None]
                    logging.info("Got {} unassigned open issues for {}".format(len(prs), repo))
                    for pr in prs:
                        pr_owner = pr.user.login
                        next_assignee, user_rota = first_not(user_rota, pr_owner)
                        logging.info("Assigning {} #{} to {}".format(repo, pr.number, next_assignee))
                        pr.assign(next_assignee)
                        logging.info("Assigned {} #{} to {}".format(repo.name, pr.number, next_assignee))
            except Exception as e:
                logging.error("Error talking to github, waiting a bit. Error was {}".format(e))
            logging.info("Sleeping for 10 mins.")
            sleep(args.poll_interval)
    except FileNotFoundError:
        logging.error("Couldn't find token file {}, do you need to run pullbot-auth?".format(args.token_file))
    except Exception as e:
        logging.error(e)

