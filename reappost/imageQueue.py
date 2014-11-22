import Queue
from multiprocessing import Process, Pipe
import imgmatcher

def mkNewImgQueue(mainPipe,recvPipe,queueLock,imgLink,maxNumAgents):
	queue = ImageQueue(mainPipe,recvPipe,queueLock,imgLink,maxNumAgents)
	queue.run()

class ImageQueue:

	def __init__(self,mainPipe,recvPipe,queueLock,origImgLink,maxNumAgents):
		self.imgLink = origImgLink
		self.queue = Queue.LifoQueue()
		self.mainPipe = mainPipe
		self.recvPipe = recvPipe
		self.queueLock = queueLock
		self.pipeBusy = []
		#create numAgents pipes
		self.numAgents = maxNumAgents
		self.processPipes = []
		self.dispatches = 0
		self.expectingScrapes = True
		
		#initialize processes and pass the pipe
		for i in xrange(0,maxNumAgents):
			ourpipe, theirpipe = Pipe(True)
			self.processPipes.append(ourpipe)
			self.pipeBusy.append(True)
			p = Process(target=imgmatcher.mkNewImgMatcher,
						args= (i+1,self.mainPipe,theirpipe,self.queueLock,self.imgLink))
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
			for i in xrange(0,len(self.processPipes)):
				if not self.pipeBusy[i]:
					self.sendToPipe(i)
					return

	def sendToPipe(self,i):
		self.pipeBusy[i] = True
		self.dispatches += 1
		self.processPipes[i].send(("NEWIMG",self.pop()))

	#first check if queue empty
	def checkQueueAndSendToPipe(self,index):
		if not self.queueEmpty():
			self.sendToPipe(index)

	#receive from Reddit Scraper and from ImageProcessorWorkers
	def run(self):
		try:
			while True:
				if self.didWorkAndDone():
					for lepipe in self.processPipes:
						lepipe.send(('HALT', None))
					self.mainPipe.send(None)
					break
				result = self.recvPipe.recv()
				#if result != None:
				(pid,msg) = result
				#check queue and send to workers appropriately
				if pid == 0:#Reddit Scraper
					if msg == None:
						self.expectingScrapes = False
					else:
						self.push(msg)
				elif msg == "NEWIMG":
					self.pipeBusy[pid-1] = False
				self.sendToArbitraryPipe()
		except IOError:
			print('IOError')
			
	def didWorkAndDone(self):
		if self.dispatches > 0 and not self.expectingScrapes:
			done = True
			for busy in self.pipeBusy:
				if busy:
					done = False
					break
			return done
		return False

#test image queue

