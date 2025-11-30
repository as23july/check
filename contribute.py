#!/usr/bin/env python
import argparse
import os
from datetime import datetime
from datetime import timedelta
from random import randint
from subprocess import Popen
import sys


def main(def_args=sys.argv[1:]):
    args = arguments(def_args)
    curr_date = datetime.now()

    repository = args.repository
    user_name = args.user_name
    user_email = args.user_email

    # -------- Use existing folder instead of making a new one --------
    if repository is None:
        sys.exit("Error: You must provide --repository")

    start = repository.rfind('/') + 1
    end = repository.rfind('.')
    directory = repository[start:end]

    # Ensure folder exists
    if not os.path.exists(directory):
        sys.exit(f"Folder '{directory}' does not exist. Clone or create it first.")

    os.chdir(directory)

    # If repo is not initialized, initialize it
    if not os.path.exists(".git"):
        run(['git', 'init', '-b', 'main'])

    # Set git config
    if user_name is not None:
        run(['git', 'config', 'user.name', user_name])

    if user_email is not None:
        run(['git', 'config', 'user.email', user_email])

    no_weekends = args.no_weekends
    frequency = args.frequency
    days_after = args.days_after

    # -------- Commit Dates: From 23 Nov → Today --------
    year = curr_date.year
    start_date = datetime(year, 11, 23, 20, 0)

    days_before = (curr_date - start_date).days
    if days_before < 0:
        sys.exit("23 November is in the future!")

    for day in (start_date + timedelta(n) for n in range(days_before + days_after + 1)):
        if (not no_weekends or day.weekday() < 5) and randint(0, 100) < frequency:
            for commit_time in (day + timedelta(minutes=m)
                                for m in range(contributions_per_day(args))):
                contribute(commit_time)

    # Add remote if not added
    run(['git', 'remote', 'add', 'origin', repository], silent=True)

    # Push changes
    run(['git', 'branch', '-M', 'main'])
    run(['git', 'push', '-u', 'origin', 'main'])

    print('\nRepository updated '
          '\x1b[6;30;42msuccessfully\x1b[0m!')


def contribute(date):
    with open(os.path.join(os.getcwd(), 'README.md'), 'a') as file:
        file.write(message(date) + '\n\n')
    run(['git', 'add', '.'])
    run(['git', 'commit', '-m', '"%s"' % message(date),
         '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])


def run(commands, silent=False):
    try:
        if silent:
            Popen(commands, stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w')).wait()
        else:
            Popen(commands).wait()
    except:
        pass


def message(date):
    return date.strftime('Contribution: %Y-%m-%d %H:%M')


def contributions_per_day(args):
    max_c = args.max_commits
    max_c = min(max_c, 20)
    max_c = max(max_c, 1)
    return randint(1, max_c)


def arguments(argsval):
    parser = argparse.ArgumentParser()
    parser.add_argument('-nw', '--no_weekends', action='store_true', default=False)
    parser.add_argument('-mc', '--max_commits', type=int, default=10)
    parser.add_argument('-fr', '--frequency', type=int, default=80)
    parser.add_argument('-r', '--repository', type=str, required=True)
    parser.add_argument('-un', '--user_name', type=str, required=False)
    parser.add_argument('-ue', '--user_email', type=str, required=False)
    parser.add_argument('-da', '--days_after', type=int, default=0)
    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()
