from __future__ import print_function
import sys
import cv2
from random import randint
import imutils
from imutils.object_detection import non_max_suppression
import numpy as np
import people

class container():
	
	def __init__(self):
		self.trackers = {}
		self.people = {}
		
	def add(self, tracker, tnum, frame, bbox, color):
		tracker.init(frame, bbox)
		p = people.person(tnum, bbox, color)
		self.trackers[tnum] = tracker
		self.people[tnum] = p
		return p
	
	def update(self, frame):
		bools = []
		bboxes = []
		ids = []
		peo = []
		for k, v in self.trackers.items():
			boo, bbox = v.update(frame)
			self.people[k].update(bbox)
			peo.append(self.people[k])
			bools.append(boo)
			bboxes.append(bbox)
			ids.append(k)
		return bools, bboxes, ids, peo
	
	def remove(self, ID):
		self.people[ID].deleteSelf()
		del self.trackers[ID]
		print("done!")