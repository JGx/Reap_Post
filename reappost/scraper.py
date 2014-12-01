import praw
import argparse
import imageQueue
from time import sleep
from multiprocessing import Process, Pipe, Lock

class Scraper:

	def __init__(self,subreddit,imgLink,numPosts,threshold,num_workers):
		#check if python build script works in sublime
		if imgLink == None:
			print "Received None imgLink"
			return

		self.r = praw.Reddit(user_agent="reappost")
		self.subreddit = subreddit
		self.numPosts = numPosts
		self.imgLink = imgLink
		ourpipe, theirpipe = Pipe()
		self.queueLock = Lock()
		self.queuepipe = ourpipe
		self.queue = Process(target=imageQueue.mkNewImgQueue,
						args=(self.queuepipe,theirpipe,self.queueLock,imgLink,threshold,num_workers))#<-- change num workers here
		return

	# Scrapes the given subreddit for the latest 25 hot posts
	def run(self):
		#scrape all desired posts and store them in a list
		self.queue.start()
		self.scrape()
		self.queueLock.acquire(True)
		self.queuepipe.send((0, None))
		self.queueLock.release()
		self.queue.join()

	def scrape(self):
		subreddit = self.r.get_subreddit(self.subreddit)
		#we need to get relevant content, not get_hot
		for post in subreddit.get_hot(limit=self.numPosts):
			#only create entry if this post is an image
			if isImgurPost(post):	
				self.queueLock.acquire(True)
				self.queuepipe.send((0,RedditPost(post)))
				self.queueLock.release()
				

def isImgurPost(submission):
	return "i.imgur" in submission.url and not submission.url.endswith('.gifv')


class RedditPost:

	def __init__(self, submission):
		self.url = submission.url
		self.title = submission.title
		self.score = submission.score
		self.num_comments = submission.num_comments
		return

	# prints the info about this post
	def info(self):
		return {'url':self.url, 'title':self.title, 'score':self.score, 'comments':self.num_comments}

if __name__ == '__main__':
	#Parser asks user for subreddit to pull from
	parser = argparse.ArgumentParser(description='Reap Post')
	parser.add_argument('-S', dest='subreddit',  required=True)
	parser.add_argument('-I', dest='imgLink',  required=True)
	parser.add_argument('-N', dest='numPosts', type=int, required=False, default=100)
	parser.add_argument('-T', dest='threshold', type=float, required=False, default=0.05)
	parser.add_argument('-W', dest='numWorkers', type=int, required=False, default=20)
	args = vars(parser.parse_args())
	subreddit = args['subreddit']
	imgLink = args['imgLink']
	numPosts = args['numPosts']
	threshold = args['threshold']
	num_workers = args['numWorkers']
	scraper = Scraper(subreddit,imgLink,numPosts,threshold,num_workers)
	scraper.run()
