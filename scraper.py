import praw
import argparse

#Parser asks user for subreddit to pull from
parser = argparse.ArgumentParser(description='Reap Post')
parser.add_argument('-S', dest='subreddit',  required=True)

p = vars(parser.parse_args())
subreddit = p['subreddit']

print subreddit

r = praw.Reddit(user_agent="reappost")
submissions = r.get_subreddit(subreddit).get_hot(limit=25)

for x in submissions:
	print str(x)
