import Queue
from multiprocessing import Process, Pipe
import imgmatcher

class ImageQueue:
	
	def mkNewImgQueue(pipe,imgLink,maxNumAgents):
		queue = ImageQueue(pipe,imgLink,maxNumAgents)
		queue.run()

	def __init__(self,mainPipe,origImgLink,maxNumAgents):
		self.imgLink = origImgLink
		self.queue = Queue.LifoQueue()
		self.mainPipe = mainPipe
		self.pipeBusy = []
		#create numAgents pipes
		self.numAgents = maxNumAgents
		self.processPipes = []
		for i in xrange(0,maxNumAgents):
			pipein, pipeout = Pipe(False)
			self.processPipes.append([pipein,pipeout])
			self.pipeBusy[i] = False
		#initialize processes and pass the pipe
		for i in xrange(0,maxNumAgents):
			p = Process(target=mkNewImgMatcher,
						args= (i,self.processPipes[i][1],self.imgLink))
			p.start()
			#p.join()
		return


	def push(self,img):
		self.queue.put(img)

	def pop(self):
		return self.queue.get()

	def queueEmpty(self):
		return self.queue.empty()

	def printElems(self):
		for elem in iter(self.queue.get,None):
			print elem

	def pollAllPipes(self):

		for pipe in self.processPipes:
			pipeIn = pipe[0]
			gotMail = pipeIn.poll()
			if gotMail:
				return pipe.recv()
		#query the reddit scraper pipe
		newImg = self.mainPipe.poll()
		if newImg:
			return self.mainPipe.recv()
		#nothing in any pipe
		return None

	def sendToArbitraryPipe(self):
		#check if queue empty
		if self.queueEmpty() == False:
			#if not empty, pop and send to first available pipe
			for i in xrange(0,len(self.processPipes.length)):
				if self.pipeBusy[i] == False:
					self.sendToPipe(i)
					return


	def sendToPipe(self,pid):
		self.pipeBusy[i] = True
		self.processPipes[i].send("NEWIMG",self.pop())

	#first check if queue empty
	def checkQueueAndSendToPipe(self,pid):
		if self.queueEmpty() == False:
			self.sendToPipe(pid)

	#receive from Reddit Scraper and from ImageProcessorWorkers
	def run(self):
		try:
			while True:
				result = self.pollAllPipes()
				if result != None:
					(pid,msg) = result
					#check queue and send to workers appropriately
					sendToArbitraryPipe()
					if pid == 0:#Reddit Scraper
						self.push(msg)
					elif msg == "NEWIMG":
						self.sendToPipe(pid)
		except IOError:
			print 'IOError'

#test image queue

