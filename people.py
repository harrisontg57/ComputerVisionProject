from __future__ import print_function
import sys
import cv2
from random import randint
import imutils
from imutils.object_detection import non_max_suppression
import numpy as np
import groupHolder

class person():
	def __init__(self, ID, bbox, color):
		self.color = color
		self.ID = ID
		self.center = (bbox[0]+bbox[2]/2, bbox[1]+bbox[3]/2)
		self.box = bbox
		self.velocities = []
		self.N = 0
		self.still = False
		self.group = groupHolder.group(self)
		
	def update(self, bbox):
		self.N += 1
		oldC = self.center
		self.center = (bbox[0]+bbox[2]/2, bbox[1]+bbox[3]/2)
		self.box = bbox
		self.velocities.append((self.center[0] - oldC[0], self.center[1] - oldC[1]))
		#if self.N > 10: self.colorByV(1.0,10)
	
	def setGroup(self, g):
		g.add(self)
		self.group = g
		
	def removeFromGroup(self):
		self.group.remove(self)
		self.group = groupHolder.group(self)
		
	def deleteSelf(self):
		self.removeFromGroup()
		
		
	def getAvgV(self, n):
		if self.N < n: return self.velocities[len(self.velocities)-1]
		l = len(self.velocities) - 1
		avg = [0.0,0.0]
		c = n
		while n > 0:
			v = self.velocities[l - n]
			avg[0] += v[0]
			avg[1] += v[1]
			
			n -= 1
		return (avg[0]/c, avg[1]/c)
	
	def changeColor(self, newColor):
		self.color = newColor
		
	def colorByV(self, thresh, n):
		v = self.getAvgV(n)
		if v[0] > 0:
			R = 255 * abs(v[0])
			B = 0
		else:
			R = 0
			B = 255 * abs(v[0])
			
		if v[1] > 0: G = 125 + 125 * abs(v[1])
		else: G = 125 * abs(v[1])
		#B = 100
		self.changeColor((G, B, R))
		#if abs(v[0]) < thresh and abs(v[1]) < thresh:
		#	self.changeColor((255,255,255))
		#	self.still = True
			
	def getID(self):
		return self.ID
	
	def getAge(self):
		return self.N
			
	def isStill(self):
		return self.still
	
	def getGroup(self):
		return self.group
	
	def getCenter(self):
		return (int(self.center[0]),int(self.center[1]))
		
	def getColor(self):
		return self.color
	
	def getBox(self):
		return self.box
