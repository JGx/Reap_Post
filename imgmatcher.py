from PIL import Image
import urllib, cStringIO
from multiprocessing import Process, Pipe

def mkNewImgMatcher(queuePipe, originalImage):
	matcher = ImgMatcher(queuePipe, originalImage)
	matcher.run()

class ImgMatcher:
	
	def __init__(self, queuePipe, origImg):
		self.queuePipe = queuePipe
		self.origImg = origImg
		
	def run(self):
		try:
			while True:
				(msgType, msg) = self.queuePipe.recv()
				if msgType == 'HALT':
					self.queuePipe.close()
					return
				elif msgType == 'NEWIMG':
					img = Image.open(cStringIO.StringIO(urllib.urlopen(msg).read()))
					imgdata = list(img.getdata())
					if len(self.origImg) != len(imgdata):
						print("Images did NOT match")
					else:
						match = True
						for i in range(0,len(imgdata)):
							(ra,ga,ba) = self.origImg[i]
							(rb,gb,bb) = imgdata[i]
							if ra != rb or ga != gb or ba != bb:
								print("Images did NOT match")
								match = False
								break
						if match:
							print("Images did INDEED match")
		except IOError as e:
			print("I/O error({0}): {1}".format(e.errno, e.strerror))
	
def start():
	orig = Image.open(cStringIO.StringIO(urllib.urlopen("http://i.imgur.com/dMfco99.jpg").read()))
	myPipe, yourPipe = Pipe()
	match = Process(target=mkNewImgMatcher, args=(yourPipe, list(orig.getdata())))
	match.start()
	myPipe.send(("NEWIMG", "http://i.imgur.com/x4ZxyBQ.jpg"))
	myPipe.send(("HALT", None))
	match.join()

if __name__ == '__main__':    
    start()