from itertools import cycle, count, chain
from time import sleep
import argparse
from github3 import login
import logging
import warnings

from pullbot.util import get_log_level
from pullbot import __version__

parser = argparse.ArgumentParser("PullBot", description="A bot for automating GitHub Pull Requests.")
parser.add_argument("token_file", type=str, help="Path to a file containing a GitHub token.")
parser.add_argument("-r", "--repos", type=str, nargs="+", help="Repositories to watch", required=True)
parser.add_argument("-u", "--users", type=str, nargs="+", help="Users to rota.", required=True)
parser.add_argument("-n", "--n-reviewers", type=int, help="Number of reviewers to assign to each PR.", default=1)
parser.add_argument('-m', '--mandatory-reviewers', type=str, nargs="+", help="Reviewers to always assign (unless conflicted).", default=[])
parser.add_argument("-v", "--verbosity", action="count", default=0)
parser.add_argument("-i", "--poll-interval", type=int, help="Seconds to wait between checks.", default=600)
parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))


def take_not(rota, user, n):
    """
    Take n users from the rota who are not user, and
    put user a the front of the queue.

    :param rota:
    :param user:
    :param n:
    :return:
    """
    rotad = set()
    while len(rotad) < n:
        assignee, rota = first_not(rota, user)
        rotad.add(assignee)
    return rotad, rota


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
    args.users = set(args.users)
    args.mandatory_reviewers = set(args.mandatory_reviewers)
    args.repos = set(args.repos)
    if(args.n_reviewers >= len(args.users)):
        parser.error("Number of assignees per PR is too high for number of reviewers.")
    if(args.n_reviewers > 1):
        warnings.warn("More than one asssignee not currently supported :(.")
        args.n_reviewers = 1
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
                        assignees, user_rota = take_not(user_rota, pr_owner, args.n_reviewers)
                        assignees.update(args.mandatory_reviewers)
                        logging.info("Assigning {} #{} to {}".format(repo, pr.number, assignees))
                        #pr.edit(assignees=assignees)
                        pr.assign(assignees.pop()) # Disable multiply assigns while github3.py new release pending
                        logging.info("Assigned {} #{} to {}".format(repo.name, pr.number, assignees))
            except Exception as e:
                logging.error("Error talking to github, waiting a bit. Error was {}".format(e))
            logging.info("Sleeping for {}s.".format(args.poll_interval))
            sleep(args.poll_interval)
    except FileNotFoundError:
        logging.error("Couldn't find token file {}, do you need to run pullbot-auth?".format(args.token_file))
    except Exception as e:
        logging.error(e)

