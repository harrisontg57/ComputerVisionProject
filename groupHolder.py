from __future__ import print_function
import sys
import cv2
import random
import imutils
from imutils.object_detection import non_max_suppression
import numpy as np
import people

random.seed("krazy")

class group():
	def __init__(self, peep):
		self.gid = random.randint(0, 9999999)
		self.cm = peep.getCenter()
		r = random.randint(0,200)
		g = random.randint(0,200)
		self.color = (0, random.randint(g, 255), random.randint(r, 255))
		self.ppl = []
		self.ppl.append(peep)
		self.popu = 1
		self.N = 0
	
	def add(self, peep):
		self.ppl.append(peep)
		self.popu += 1
		self.update()
	
	def remove(self, peep):
		self.ppl.remove(peep)
		self.popu -= 1
		#peep.removeFromGroup()
		#print(len(self.ppl))
		self.update()
		
	def update(self):
		if len(self.ppl) == 0: return
		if len(self.ppl) == 1: return
		c = [0.0,0.0]
		for i, p in enumerate(self.ppl):
			pc = p.getCenter()
			c[0] += pc[0]
			c[1] += pc[1]
		self.cm = (c[0]/i,c[1]/i)
		self.N += 1
		
	def getAge(self):
		return self.N
		
	def getMembers(self):
		return self.ppl
		
	def getSize(self):
		return self.popu
	
	def getCenter(self):
		return self.cm
	
	def getColor(self):
		return self.color
	
	def getGID(self):
		return self.gid