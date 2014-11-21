from PIL import Image
import urllib, cStringIO
from multiprocessing import Process, Pipe
import scraper
import requests

def mkNewImgMatcher(pid, queuePipe, origImgUrl, threshold=0.95):
	originalImage = Image.open(cStringIO.StringIO(urllib.urlopen(origImgUrl).read()))
	matcher = ImgMatcher(pid, queuePipe, originalImage, threshold)
	matcher.run()

class ImgMatcher:
	
	def __init__(self, pid, queuePipe, origImg, threshold):
		self.queuePipe = queuePipe
		self.origImg = origImg
		self.pid = pid
		self.threshold = threshold
		
	def run(self):
		try:
			while True:
				self.queuePipe.send((self.pid, 'NEWIMG'))
				(msgType, msg) = self.queuePipe.recv()
				if msgType == 'HALT':
					self.queuePipe.close()
					return
				elif msgType == 'NEWIMG':
					img = Image.open(cStringIO.StringIO(urllib.urlopen(msg.url).read()))
					imgdata = list(img.getdata())
					if len(self.origImg) != len(imgdata):
						sendResult(False, msg)
					else:
						similarity = compareImage(imgdata)
						if similarity >= self.threshold:
							sendResult(True, msg)
		except IOError as e:
			print("I/O error({0}): {1}".format(e.errno, e.strerror))
	
	def compareImage(otherImg):
		datalen = len(otherImg)
		for i in range(0,datalen):
			(ra,ga,ba) = self.origImg[i]
			(rb,gb,bb) = imgdata[i]
			if ra != rb or ga != gb or ba != bb:
				match = False
				break
				
	def sendResult(match, msg):
		#return requests.get('', params={'url':msg.url, 'score':msg.score, 'title':msg.title, 'num_comments':msg.num_comments, 'match':match})
		params={'url':msg.url, 'score':msg.score, 'title':msg.title, 'num_comments':msg.num_comments, 'match':match}
		print(params)