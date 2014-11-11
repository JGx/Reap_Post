import praw
import argparse
from time import sleep

#Parser asks user for subreddit to pull from
parser = argparse.ArgumentParser(description='Reap Post')
parser.add_argument('-S', dest='subreddit',  required=True)
parser.add_argument('-N', dest='numScrapes', type=int, required=False)
args = vars(parser.parse_args())
subreddit = args['subreddit']
numScrapes = 1
if args['numScrapes']!=None:
	#need to check for valid time -- TODO LATER
	numScrapes = args['numScrapes']

class Scraper:

	def __init__(self,subreddit,numScrapes):
		self.r = praw.Reddit(user_agent="reappost")
		self.subreddit = subreddit
		self.numScrapes = numScrapes
		return

	# Scrapes the given subreddit for the latest 25 hot posts
	def run(self):
		imgurPosts =[]
		#request every 2 seconds until numScrapes is reached
		for scrape in range(0,self.numScrapes):
			print 'Scrape #',scrape
			imgurPosts+=self.scrape()
			sleep(2)
		
		#print all posts titles
		for p in imgurPosts:
			print p.title

	def scrape(self):
		imgurPosts = []
		submissions = self.r.get_subreddit(self.subreddit).get_hot(limit=25)
		for x in submissions:
			#only create entry if this post is an image
			if isImgurPost(x):
				imgurPosts.append(RedditPost(x))
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


scraper = Scraper(subreddit,numScrapes)
scraper.run()
