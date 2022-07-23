import datetime
import os

import praw

DEFAULT_SUBREDDIT_NAME = 'synthesizers'

MAX_AGE_TO_PROCESS = 3  # max age of post to process in minutes
MAX_SUBMISSIONS_TO_LOOKBACK = 10  # max number of submissions per author to scan
MAX_SUBMISSIONS_TO_PROCESS = 5  # max number of new submissions to scan
POST_WINDOW_MINUTES = 5  # minutes between crossposts to consider spam
SPAM_THRESHOLD = 5  # number of other subs posted to to consider spam


class SynthsSpamBot:
    def __init__(self, subreddit_name=DEFAULT_SUBREDDIT_NAME, dry_run=False):
        self.dry_run = dry_run

        self.reddit = praw.Reddit('SynthsSpamBot')
        self.subreddit = self.reddit.subreddit(subreddit_name)

    def scan(self):
        for submission in self.subreddit.new(limit=MAX_SUBMISSIONS_TO_PROCESS):
            if self.calc_submission_age(submission) <= MAX_AGE_TO_PROCESS:
                self.process_submission(submission)

    def process_submission(self, submission):
        subreddits = set()
        submission_age = self.calc_submission_age(submission)
        author = submission.author

        for other_submission in author.submissions.new(limit=MAX_SUBMISSIONS_TO_LOOKBACK):
            other_submission_age = self.calc_submission_age(other_submission)

            if (other_submission.subreddit.display_name != DEFAULT_SUBREDDIT_NAME
                    and other_submission.title == submission.title
                    and abs(other_submission_age - submission_age) <= POST_WINDOW_MINUTES):
                subreddits.add(other_submission.subreddit.display_name)

        count = len(subreddits)
        if count >= SPAM_THRESHOLD:
            self.log('Flagged as crosspost spam', submission, count)
            if not self.dry_run:
                mod_note = f'Flagged as crosspost spam. Posted to {count} other subreddits.'
                submission.mod.remove(mod_note=mod_note)

    @ staticmethod
    def is_actionable(submission):
        return (not submission.distinguished == 'moderator'
                and not submission.approved
                and not submission.removed
                and not submission.locked)

    @ staticmethod
    def calc_submission_age(submission):
        now = datetime.datetime.now()
        created = datetime.datetime.fromtimestamp(submission.created_utc)
        age = now - created

        return age.total_seconds() / 60

    def log(self, message, submission, count):
        is_dry_run = '*' if self.dry_run is True else ''
        name = type(self).__name__
        now = datetime.datetime.now()
        print(f'{is_dry_run}[{name}][{now}] {message}: "{submission.title}" ({count}) ({submission.id})')


def lambda_handler(event=None, context=None):
    subreddit_name = os.environ['subreddit_name'] if 'subreddit_name' in os.environ else DEFAULT_SUBREDDIT_NAME
    dry_run = os.environ['dry_run'] == 'True' if 'dry_run' in os.environ else False
    bot = SynthsSpamBot(subreddit_name=subreddit_name, dry_run=dry_run)
    bot.scan()


if __name__ == '__main__':
    lambda_handler()
