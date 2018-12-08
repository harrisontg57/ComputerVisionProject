from __future__ import print_function
import sys
import cv2
from random import randint
import imutils
from imutils.object_detection import non_max_suppression
import numpy as np
import trackContainer
import people
import groupHolder
import math

 
#print(cv2.__version__)
#print(cv2.getBuildInformation())
trackerTypes = ['BOOSTING', 'MIL', 'KCF','TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
 
def createTrackerByName(trackerType):
# Create a tracker based on tracker name
	if trackerType == trackerTypes[0]:
		tracker = cv2.TrackerBoosting_create()
	elif trackerType == trackerTypes[1]: 
		tracker = cv2.TrackerMIL_create()
	elif trackerType == trackerTypes[2]:
		tracker = cv2.TrackerKCF_create()
	elif trackerType == trackerTypes[3]:
		tracker = cv2.TrackerTLD_create()
	elif trackerType == trackerTypes[4]:
		tracker = cv2.TrackerMedianFlow_create()
	elif trackerType == trackerTypes[5]:
		tracker = cv2.TrackerGOTURN_create()
	elif trackerType == trackerTypes[6]:
		tracker = cv2.TrackerMOSSE_create()
	elif trackerType == trackerTypes[7]:
		tracker = cv2.TrackerCSRT_create()
	else:
		tracker = None
		print('Incorrect tracker name')
		print('Available trackers are:')
		for t in trackerTypes:
			print(t)
 
	return tracker

def distance(a,b):
	#print(int(a[0] - b[0])^2 , int(a[1] - b[1])^2)
	x = abs((a[0] - b[0])**2)
	y = abs((a[1] - b[1])**2)
	#print(x + y)
	return math.sqrt(x + y)

def closeV(a, b):
	s = distance(a,b)
	x = abs(a[0] - b[0])
	y = abs(a[1] - b[1])
	if x < .33 and y < .33: return True
	return False
	#if s < .5: return True
	#return False

def whoFurther(a, b):
	grp = a.getGroup()
	ad = distance(a.getCenter(), grp.getCenter())
	bd = distance(b.getCenter(), grp.getCenter())
	#add velocity difference from group v
	if ad > bd: return a, b
	else: return b, a
	


def checkGroup(p,ppl):
	for i, ps in enumerate(ppl):
		pc = p.getCenter()
		psc = ps.getCenter()
		if p == ps: continue
		if p.getGroup() == ps.getGroup():
			if distance(pc, psc) > 150:
				if p.getGroup().getSize() == 2:
					p.removeFromGroup()
					ps.removeFromGroup()
				if p.getGroup().getSize() > 2:
					f, c = whoFurther(p,ps)
					f.removeFromGroup()
					
			#	f, c = whoFurther(p,ps)
			#	c.getGroup().remove(f)
			#	groups.append(f.getGroup())
			elif p.getGroup().getSize() == 2 and p.getAge() > 12 and ps.getAge() > 12 and not closeV(p.getAvgV(12), ps.getAvgV(12)):
					f, c = whoFurther(p,ps)
					f.removeFromGroup()
					c.removeFromGroup()
					
			pass
			continue

		if distance(pc, psc) < 75:
			#print('True')
			#print(p.getCenter(), ps.getCenter(), distance(pc, psc))
			pv = p.getAvgV(10)
			psv = ps.getAvgV(10)
			if closeV(pv, psv):
				#print("Close Velocity")
				#print(pv, psv, closeV(pv, psv))
				try: groups.remove(ps.getGroup())
				except: 1
				ps.getGroup().remove(ps)
				ps.setGroup(p.getGroup())
				p.setGroup(ps.getGroup())
				
videoPath = "mall.mp4"
cap = cv2.VideoCapture(videoPath)
success, frame = cap.read()
if not success:
	print('Failed to read video')
	sys.exit(1)

bboxes = []
colors = []

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

(rects, weights) = hog.detectMultiScale(frame, winStride=(4,4),padding=(16,16), scale=1.05, useMeanshiftGrouping=True)
for (x,y,w,h) in rects:
	cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 0, 255), 2)
	bbox = (x,y,w,h)
	#bbox = (x+w/6,y+h/4,w/3,h/4)
	bboxes.append(bbox)


#rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
#pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
#for (xA, yA, xB, yB) in pick:
#	cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
#	bbox = (xA, yA, xB, yB)
#	bboxes.append(bbox)
#	colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
cv2.imshow('MultiTracker', frame)
cv2.waitKey(0)

# Specify the tracker type
trackerType = "CSRT" 
 
# Create Tracker Container
multiTracker = trackContainer.container()

window = cv2.getWindowImageRect('MultiTracker')

it = 0

colors = {}
peps = {}
groups = []
for bbox in bboxes:
	trk = createTrackerByName(trackerType)
	p = multiTracker.add(trk, it, frame, bbox, (255,0,0))
	#((randint(0, 255), randint(0, 255), randint(0, 255)))
	peps[it] = p
	groups.append(p.getGroup())
	it += 1
	
def getCenter(bbox):
	return (bbox[0]+bbox[2]/2, bbox[1]+bbox[3]/2)

def hasNoInside(nboxes,x,y,w,h):
	for i, newbox in enumerate(nboxes):
		center = getCenter(newbox)
		if (center[0] > x and center[1] > y and center[0] < x + w and center[1] < y + h):
			return False
		if (int(newbox[0]) > x - 25) and (int(newbox[1]) > y - 25) and (int(newbox[0] + newbox[2]) < x + w + 25) and (int(newbox[1] + newbox[3]) < y + h + 25):
			return False
	return True

def merge(ppl,x,y,w,h):
	for i, p in enumerate(ppl):
		hits = []
		center = p.getCenter()
		if (center[0] > x - 25 and center[1] > y - 25 and center[0] < x + w + 25 and center[1] < y + h + 25):
			hits.append(p)
		if len(hits) > 1:
			multiTracker.add(createTrackerByName(trackerType),it,frame,(x,y,w,h), (255,0,0))
			for np in hits:
				np.deleteSelf()
				multiTracker.remove(np.getID())
			

count = 0

	
	
while cap.isOpened():
	success, frame = cap.read()
	if not success:
		break


# get updated location of objects in subsequent frames
	success, boxes, ids, ppl = multiTracker.update(frame)
	for m, b in enumerate(success):
		if not b:
			multiTracker.remove(ids[m])
			

	if count%20 == 0:
		#frame2 = frame #.clone()
		stuff = frame.shape
		#cv2.rectangle(frame2, (stuff[0]/6, 0), (stuff[0]*5/6, stuff[1]), (0,255,0), -1)
		(rects, weights) = hog.detectMultiScale(frame[:,:,:], winStride=(2,2),padding=(16,16), scale=1.05, useMeanshiftGrouping=True)
		for (x,y,w,h) in rects:
			#cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 0, 255), 2)
			if hasNoInside(boxes,x,y,w,h):
				p = multiTracker.add(createTrackerByName(trackerType),it,frame,(x,y,w,h), (255,0,0))
				colors[it] = ((randint(0, 255), randint(0, 255), randint(0, 255)))
				peps[it] = p
				groups.append(p.getGroup())
				it += 1
#		if count%10 == 0:
#			for (x,y,w,h) in rects:
#				merge(ppl,x,y,w,h)
				
	if count%6 == 0:

		for i, pers in enumerate(ppl):
			checkGroup(pers,ppl)
			peps[ids[i]] = pers
			box = pers.getBox()
			p1 = (int(box[0]), int(box[1]))
			p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
			if pers.getGroup().getSize() > 1:
				cv2.circle(frame,pers.getCenter(),10,pers.getGroup().getColor(), 1)
			else:
				cv2.rectangle(frame, p1, p2, pers.getColor(), 2, 1)
			#for grp in groups:
			#	if grp.getSize() > 1:
			#		for j,p in enumerate(grp.getMembers()):
			#			if j == len(grp.getMembers()) -1: break
			#			cv2.line(frame, p.getCenter(), grp.getMembers()[j+1].getCenter(), grp.getColor())
			#if not pers.isStill():
			#	cv2.circle(frame,pers.getCenter(),5,pers.getColor(),-1)
		#cv2.imshow('MultiTracker', frame)
		#cv2.waitKey(0)

# draw tracked objects
	for i, pers in enumerate(ppl):
		peps[ids[i]] = pers
		box = pers.getBox()
		p1 = (int(box[0]), int(box[1]))
		p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
		if pers.getGroup().getSize() > 1:
			pers.getGroup().update()
			cv2.circle(frame,pers.getCenter(),10,pers.getGroup().getColor(), 3)
			for j,p in enumerate(pers.getGroup().getMembers()):
				if j == len(pers.getGroup().getMembers()) -1: break
				cv2.line(frame, p.getCenter(), pers.getGroup().getMembers()[j+1].getCenter(), pers.getGroup().getColor(),3)
				#d = distance(p.getCenter(), pers.getGroup().getMembers()[j+1].getCenter())
				#cv2.putText(frame,'Separation: '+str(d), p.getCenter(), 2, 1, (0,0,0))
		else:
			cv2.rectangle(frame, p1, p2, pers.getColor(), 2, 1)
		#for grp in groups:
		#	if grp.getSize() > 1:
		#		for j,p in enumerate(grp.getMembers()):
		#			if j == len(grp.getMembers()) -1: break
		#			cv2.line(frame, p.getCenter(), grp.getMembers()[j+1].getCenter(), grp.getColor(), 1)
		#if not pers.isStill():
		#	cv2.circle(frame,pers.getCenter(),10,pers.getColor(),-1)
		
		
		#Where we send trackers when they get too old...
		if p1[0] < -20 or p1[1] < -20: 
			pers.deleteSelf()
			multiTracker.remove(ids[i])
		elif p2[0] > window[2]+20 or p2[1] > window[3]+20: 
			pers.deleteSelf()
			multiTracker.remove(ids[i])

	#video.write(frame)
	cv2.imwrite('./mallFullROI/mall'+str(count)+'.png',frame)
	cv2.imshow('MultiTracker', frame)
 
	count += 1
# quit on ESC button
	if cv2.waitKey(1) & 0xFF == 27:# Esc pressed
		break
