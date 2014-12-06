# Reap_Post

A Reddit Repost Checker

Files to use (all in the reappost subdirectory):

scraper.py - Scrapes reddit for batches of posts and puts them in the image queue.  Entry point for the program.
imgqueue.py - Holds the posts that are waiting to be analyzed.  Posts are removed by the image matcher.
imgmatcher.py - Checks for matches against the original image. If there is a match, informs the image queue so that
it can print it out.

Other files were intended to be for the Heroku app, which was unable to be completed.
