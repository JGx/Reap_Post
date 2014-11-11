import praw

class Scraper:

	def __init__(self):
		self.r = praw.Reddit(user_agent="reappost")
		return

	# Scrapes the given subreddit for the latest 25 hot posts
	def scrape(self):
		submissions = self.r.get_subreddit('pics').get_hot(limit=25)
		for x in submissions:
			print x.url

class Post:

	def __init__(self):
		return

	# prints the info about this post
	def info():
		print "Will add more info later"


scraper = Scraper()
scraper.scrape()