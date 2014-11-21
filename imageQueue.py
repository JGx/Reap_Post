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
		
		#initialize processes and pass the pipe
		for i in xrange(0,maxNumAgents):
			ourpipe, theirpipe = Pipe(True)
			self.processPipes.append(ourpipe)
			self.pipeBusy[i] = False
			p = Process(target=mkNewImgMatcher,
						args= (i+1,theirpipe,self.imgLink))
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
			print(elem)

	def pollAllPipes(self):
		#query the reddit scraper pipe
		if self.mainPipe.poll():
			return self.mainPipe.recv()
			
		for pipe in self.processPipes:
			if pipe.poll():
				return pipe.recv()
		
		#nothing in any pipe
		return None

	def sendToArbitraryPipe(self):
		#check if queue empty
		if not self.queueEmpty():
			#if not empty, pop and send to first available pipe
			for i in xrange(0,len(self.processPipes.length)):
				if not self.pipeBusy[i]:
					self.sendToPipe(i)
					return


	def sendToPipe(self,pid):
		self.pipeBusy[i] = True
		self.processPipes[i].send(("NEWIMG",self.pop()))

	#first check if queue empty
	def checkQueueAndSendToPipe(self,index):
		if not self.queueEmpty():
			self.sendToPipe(index)

	#receive from Reddit Scraper and from ImageProcessorWorkers
	def run(self):
		try:
			while True:
				result = self.pollAllPipes()
				if result != None:
					(pid,msg) = result
					#check queue and send to workers appropriately
					if pid == 0:#Reddit Scraper
						self.push(msg)
					elif msg == "NEWIMG":
						self.pipeBusy[pid-1] = False
				sendToArbitraryPipe()
		except IOError:
			print('IOError')

#test image queue

