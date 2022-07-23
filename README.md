# r/synthesizers Spam bot

This bot scans new posts and determines if the submission has been spammed across multiple subreddits. If so, it removes the post.

By default, the logic is as follows:

1. Check the 5 latest posts to the subreddit. As the bot runs every minute, this is sufficient. 
2. If the poster has submitted the post to 5 other subreddits within the last 5 minutes, remove the post.

# Installation

1. `pip install --user -r requirements.txt`
2. You'll need to create a personal use script on [Reddit's app portal](https://ssl.reddit.com/prefs/apps/). The developer should be a mod on the subreddit that the bot will monitor.
3. Modify praw.ini with your client id and client secret (from Reddit's app portal) along with the developer's Reddit username and password.
4. The script is stateless and does its work in one pass. It's intended to run periodically via cron or AWS Lambda, etc.
