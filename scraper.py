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

	def scrape(self):
		submissions = self.r.get_subreddit(self.subreddit).get_hot(limit=25)
		for x in submissions:
			print x.url

scraper = Scraper(subreddit)
scraper.scrape()
