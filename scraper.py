import praw
import argparse
from time import sleep

#Parser asks user for subreddit to pull from
parser = argparse.ArgumentParser(description='Reap Post')
parser.add_argument('-S', dest='subreddit',  required=True)
parser.add_argument('-N', dest='numPosts', type=int, required=False)
args = vars(parser.parse_args())
subreddit = args['subreddit']
numPosts = 100
if args['numPosts'] != None:
	#need to check for valid time -- TODO LATER
	numPosts = args['numPosts']

class Scraper:

	def __init__(self,subreddit,numPosts):
		self.r = praw.Reddit(user_agent="reappost")
		self.subreddit = subreddit
		self.numPosts = numPosts
		return

	# Scrapes the given subreddit for the latest 25 hot posts
	def run(self):
		#scrape all desired posts and store them in a list
		imgurPosts = self.scrape()
		
		#print all posts titles
		for p in imgurPosts:
			print p.title

	def scrape(self):
		imgurPosts = []
		print self.numPosts

		subreddit = self.r.get_subreddit(self.subreddit)
		for post in subreddit.get_hot(limit=self.numPosts):
			#only create entry if this post is an image
			if isImgurPost(post):
				imgurPosts.append(RedditPost(post))
		
		return imgurPosts
				

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


scraper = Scraper(subreddit,numPosts)
scraper.run()
