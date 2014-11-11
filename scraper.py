import praw

r = praw.Reddit(user_agent="reappost")
submissions = r.get_subreddit('funny').get_hot(limit=25)

for x in submissions:
	print str(x)