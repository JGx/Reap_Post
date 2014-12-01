from PIL import Image
import urllib, cStringIO
from multiprocessing import Process, Pipe
import scraper
import requests

def mkNewImgMatcher(pid, queuePipe, urlPipe, queueLock, origImgUrl, threshold):
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
		self.origImgExtrema = origImg.getextrema()
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
						self.sendResult(False, msg, 1.0)
					else:
						difference = self.compareImage(imgdata, img.getbands(), img.getextrema())
						if difference <= self.threshold:
							self.sendResult(True, msg, difference)
		except IOError as e:
			#print("I/O error({0}): {1} . {2}".format(e.errno, e.strerror, last.info()))
			pass
	
	def compareImage(self, otherImg, otherImgBands, otherExtrema):
		bandlen = len(otherImgBands)
		if len(self.origImgBands) != bandlen:
			return 1.0
		datalen = len(otherImg)
		diff = 0.0
		for i in xrange(0,datalen):
			diffs = 0.0
			if bandlen > 1:
				skip = []
				for v in xrange(0,bandlen):
					if otherExtrema[v][0] == otherExtrema[v][1]:
						skip.append(v)
				for v in xrange(0,bandlen):
					if v in skip:
						continue
					diffs += abs((self.origImg[i][v] - self.origImgExtrema[v][0]) / (self.origImgExtrema[v][1] - self.origImgExtrema[v][0]) -
							(otherImg[i][v] - otherExtrema[v][0]) / (otherExtrema[v][1] - otherExtrema[v][0]))
				diffs /= (bandlen - len(skip))
			else:
				diffs = abs((self.origImg[i] - self.origImgExtrema[0]) / (self.origImgExtrema[1] - self.origImgExtrema[0]) -
							(otherImg[i] - otherExtrema[0]) / (otherExtrema[1] - otherExtrema[0]))
			diff += diffs
		return diff / datalen

	def sendResult(self, match, msg, difference):
		params={'url':msg.url, 'score':msg.score, 'title':msg.title, 'num_comments':msg.num_comments, 'match':match, 'difference':difference}
		self.queueLock.acquire(True)
		if match:
			self.queuePipe.send((self.pid,params))
			#print(params)
		self.queueLock.release()
