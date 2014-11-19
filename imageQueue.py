import Queue
from multiprocessing import Process, Pipe
import imgmatcher

class ImageQueue:
	
	def __init__(self,mainPipe,origImgLink,maxNumAgents):
		self.imgLink = origImgLink
		self.queue = Queue.LifoQueue()
		self.mainPipe = mainPipe
		self.workerWorking = []
		#create numAgents pipes
		self.numAgents = maxNumAgents
		self.processPipes = []
		for i in xrange(0,maxNumAgents):
			pipein, pipeout = Pipe()
			self.processPipes.append([pipein,pipeout])
			self.workerWorking[i] = False
		#initialize processes and pass the pipe
		for i in xrange(0,maxNumAgents):
			p = Process(target=mkNewImgMatcher,
						args= (self.processPipes[i][1],self.imgLink))
			p.start()
			#p.join()
		return


	def push(self,img):
		self.queue.put(img)

	def pop(self):
		return self.queue.get()

	def printElems(self):
		for elem in iter(self.queue.get,None):
			print elem

	#receive from Reddit Scraper and from ImageProcessorWorkers
	def receiveLoop(self):
		try:
			while True:
				(pid,msg) = self.recv()
				if pid==0:#Reddit Scraper
					self.push(msg)
				elif msg=="NEWIMG":
					self.processPipes[pid].send(self.pop())
		except IOError:
			print 'IOError'
		self.push(img)

#test image queue
imgQ = ImageQueue(5)
imgQ.push("hey")
imgQ.printElems()