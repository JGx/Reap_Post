import Queue
from multiprocessing import Process, Pipe
import imgmatcher

def mkNewImgQueue(mainPipe,recvPipe,queueLock,imgLink,threshold,maxNumAgents):
	queue = ImageQueue(mainPipe,recvPipe,queueLock,imgLink,threshold,maxNumAgents)
	queue.run()

class ImageQueue:

	def __init__(self,mainPipe,recvPipe,queueLock,origImgLink,threshold,maxNumAgents):
		self.imgLink = origImgLink
		self.queue = Queue.LifoQueue()
		self.mainPipe = mainPipe
		self.recvPipe = recvPipe
		self.queueLock = queueLock
		self.numImages = 0
		self.pipeBusy = []
		#create numAgents pipes
		self.numAgents = maxNumAgents
		self.processPipes = []
		self.dispatches = 0
		self.expectingScrapes = True
		self.matches = []
		
		#initialize processes and pass the pipe
		for i in xrange(0,maxNumAgents):
			ourpipe, theirpipe = Pipe(True)
			self.processPipes.append(ourpipe)
			self.pipeBusy.append(True)
			p = Process(target=imgmatcher.mkNewImgMatcher,
						args= (i+1,self.mainPipe,theirpipe,self.queueLock,self.imgLink,threshold))
			p.start()
			#p.join()
		return

	def push(self,img):
		self.numImages += 1
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
					self.printFinalStats()
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
				else:
					self.printNewMatch(pid,msg)
					self.pipeBusy[pid-1] = False
				self.sendToArbitraryPipe()
		except IOError:
			#print('IOError')
			pass

	def printNewMatch(self,pid,msg):
		#add msg to list of matches for final analysis
		self.matches.append(msg)
		#pretty print current match
		print '\n'
		print 'Received new match from pipe#',pid 
		print 'Title: ',msg['title']
		print '  Url: ',msg['url']
		print 'Score: ',msg['score']
		print ' Diff: ',msg['difference']

	def printFinalStats(self):
		print '\n'
		print '-----------------------------------'
		print 'Reap Post Final Analysis:'
		print 'Out of', self.numImages,'image posts,',len(self.matches),'were reposts'
		print 'Img links in descending order of reddit post score\n'
		sortedMatches = sorted(self.matches,key = lambda match: match['score'],reverse=True)
		num = 1
		for m in sortedMatches:
			print '#', num
			num += 1
			print 'Score:', m['score']
			print 'Title:',m['title']
			print '  URL:',m['url']
			print '\n'
			
	def didWorkAndDone(self):
		if self.dispatches > 0 and not self.expectingScrapes and self.queueEmpty():
			done = True
			for busy in self.pipeBusy:
				if busy:
					done = False
					break
			return done
		return False

#test image queue

