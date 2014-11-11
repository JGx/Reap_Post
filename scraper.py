import praw
import argparse

#Parser asks user for subreddit to pull from
parser = argparse.ArgumentParser(description='Reap Post')
parser.add_argument('-S', dest='subreddit',  required=True)
p = vars(parser.parse_args())
subreddit = p['subreddit']

class Scraper:

	def __init__(self,subreddit):
		self.r = praw.Reddit(user_agent="reappost")
		self.subreddit = subreddit
		return

	# Scrapes the given subreddit for the latest 25 hot posts
	def scrape(self):
		submissions = self.r.get_subreddit(self.subreddit).get_hot(limit=25)
		for x in submissions:
			#only create entry if this post is an image
			if isImgurPost(x):
				post = RedditPost(x)
				

def isImgurPost(submission):
	return "imgur" in submission.url


class RedditPost:

	def __init__(self, submission):
		self.url = submission.url
		self.title = submission.title
		self.score = submission.score
		self.num_comments = submission.num_comments
		return

	# prints the info about this post
	def info(self):
		print "Will add more info later"


scraper = Scraper(subreddit)
scraper.scrape()
