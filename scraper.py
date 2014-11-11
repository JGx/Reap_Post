import praw

class Scraper:

	def __init__(self):
		self.r = praw.Reddit(user_agent="reappost")
		return

	def scrape(self):
		submissions = self.r.get_subreddit('pics').get_hot(limit=25)
		for x in submissions:
			print x.url

scraper = Scraper()
scraper.scrape()