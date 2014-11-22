from PIL import Image
import urllib, cStringIO
from multiprocessing import Process, Pipe
import scraper
import requests

def mkNewImgMatcher(pid, queuePipe, urlPipe, queueLock, origImgUrl, threshold=0.15):
	originalImage = Image.open(cStringIO.StringIO(urllib.urlopen(origImgUrl).read()))
	matcher = ImgMatcher(pid, queuePipe, urlPipe, queueLock, originalImage, threshold)
	matcher.run()

class ImgMatcher:
	
	def __init__(self, pid, queuePipe, urlPipe, queueLock, origImg, threshold):
		self.queuePipe = queuePipe
		self.urlPipe = urlPipe
		self.queueLock = queueLock
		self.origImg = list(origImg.getdata())
		self.origImgBands = origImg.getbands()
		self.pid = pid
		self.threshold = threshold
		
	def run(self):
		last = None
		try:
			while True:
				self.queueLock.acquire(True)
				self.queuePipe.send((self.pid, 'NEWIMG'))
				self.queueLock.release()
				(msgType, msg) = self.urlPipe.recv()
				if msgType == 'HALT':
					#self.queuePipe.close()
					self.urlPipe.close()
					return
				elif msgType == 'NEWIMG':
					last = msg
					img = Image.open(cStringIO.StringIO(urllib.urlopen(msg.url).read()))
					imgdata = list(img.getdata())
					if len(self.origImg) != len(imgdata):
						self.sendResult(False, msg)
					else:
						similarity = self.compareImage(imgdata, img.getbands())
						if similarity <= self.threshold:
							self.sendResult(True, msg)
		except IOError as e:
			print("I/O error({0}): {1} . {2}".format(e.errno, e.strerror, last.info()))
	
	def compareImage(self, otherImg, otherImgBands):
		bandlen = len(otherImgBands)
		if len(self.origImgBands) != bandlen:
			return 1.0
		datalen = len(otherImg)
		diff = 0.0
		for i in xrange(0,datalen):
			diffs = 0.0
			if bandlen > 1:
				for v in xrange(0,bandlen):
					diffs += abs(self.origImg[i][v] - otherImg[i][v])
				diffs /= bandlen
			else:
				diffs = abs(self.origImg[i] - otherImg[i])
			diff += diffs
		return diff / datalen

	def sendResult(self, match, msg):
		#return requests.get('/results', params={'url':msg.url, 'score':msg.score, 'title':msg.title, 'num_comments':msg.num_comments, 'match':match})
		params={'url':msg.url, 'score':msg.score, 'title':msg.title, 'num_comments':msg.num_comments, 'match':match}
		self.queueLock.acquire(True)
		if match:
			print(params)
		self.queueLock.release()