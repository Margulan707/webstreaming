import requests
import face_recognition
import cv2
import time
import json
import numpy as np
from PIL import Image
from datetime import datetime, timedelta
import os
import io
import imutils
from threading import Timer, Thread
import subprocess
import base64

import dbRecognition as dbR
import dbActivity as dbA
import dbMotion as dbM

auth_token='775f99089e161eb3fe19f2ff8f76a765f204c59a'
header = {'Authorization': 'Token ' + auth_token}
device_idn = "000005"
known_face_encodings = []
known_face_pk = []
unknown_face_encodings = []
unknown_face_pk = []
sended_face_pk = []
sended_unknown = []
language = 'en'
firstFrame = None
counter_motion = 0
counter_motion_first = 0
counter_internet = 0
counter_live = 0
movement_time = datetime.now()
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
frame = None
error_counter=0
time.sleep(0.2)

import psycopg2
connection = ''
# while True:
# 	try:
# 		GPIO.output(16, GPIO.LOW)
# 		GPIO.output(21, GPIO.LOW)
# 		GPIO.output(12, GPIO.LOW)
# 		r = requests.post("http://localhost:8000/api/active/devices/",
# 							headers=header,
# 							data={'device': device_idn,})
# 		json_data = json.loads(r.text)
# 		print(r.text)
# 		if json_data['success']=="YES":
# 			GPIO.output(16, GPIO.HIGH)
# 			GPIO.output(21, GPIO.HIGH)
# 			GPIO.output(12, GPIO.HIGH)
# 			break
# 		else:
# 			GPIO.output(12, GPIO.HIGH)
# 			time.sleep(0.2)
# 			GPIO.output(12, GPIO.LOW)
# 			continue
# 	except KeyboardInterrupt:
# 		break
# 	except:
# 		GPIO.output(12, GPIO.HIGH)
# 		time.sleep(0.2)
# 		GPIO.output(12, GPIO.LOW)
# 		pass

def refreshEncodings():
	global known_face_pk
	global known_face_encodings
	while True:
		try:
			print("Refresh")
			r = requests.get("http://localhost:8000/api/devices/"+device_idn+"/encodings/", headers=header)
			break
		except:
			time.sleep(20)
			pass
	json_data = json.loads(r.text)
	known_face_encodings = []
	known_face_pk = []
	for worker in json_data:
		temp = worker['faceEncodings'].split("[")[2].split("]")[0]
		known_face_encoding = np.fromstring(temp, dtype=float, sep=',')
		known_face_encodings.append(known_face_encoding)
		known_face_pk.append(worker['pk'])
	Timer(600, refreshEncodings).start()
refreshEncodings()


def refreshSendedList(delete_pk):
	global sended_face_pk
	sended_face_pk.remove(delete_pk)

def refreshUnknownList(encodings):
	unknown_face_encodings.remove(encodings)

def sendPK(name_index, frame):
	global known_face_pk
	# GPIO.output(12, GPIO.HIGH)
	image = Image.fromarray(frame)
	imgByteArr = io.BytesIO()
	image.save(imgByteArr, format='jpeg')
	imgByteArr = imgByteArr.getvalue()
	try:
		r = requests.post("http://localhost:8001/api/checks/",
			headers=header,
		 	files={'photo': imgByteArr},
		 	data={'worker':known_face_pk[name_index],
		 		'device':device_idn,
		 		'datetime':str(datetime.now())})
	except:
		dbR.insertData(device_idn, known_face_pk[name_index], str(datetime.now()))
	# GPIO.output(12, GPIO.LOW)

def sendUnknown(name_index, frame):
	# GPIO.output(21, GPIO.HIGH)
	image = Image.fromarray(frame)
	imgByteArr = io.BytesIO()
	image.save(imgByteArr, format='jpeg')
	imgByteArr = imgByteArr.getvalue()
	
	try:
		r = requests.post("http://localhost:8001/api/checks/",
			headers=header,
			files={'photo': imgByteArr},
			data={'worker':None,
				'device':device_idn,
				'datetime':str(datetime.now())})
	except:
		dbR.insertData(device_idn, None, str(datetime.now()))
	# GPIO.output(21, GPIO.LOW)

def sendMovement(time, time2):
	try:
		r = requests.post("http://localhost:8001/api/motions/",
					headers=header,
					data={'device':device_idn,
							'motion_datetime': time
							})
	except:
		dbM.insertData(device_idn, str(datetime.now()))

def sendActivity():
	try:
		print("sendAc")
		r = requests.post("http://localhost:8001/api/status/devices/",
				headers=header,
				data={'device':device_idn,
					'activity': str(datetime.now())})
	except:
		dbA.insertData(device_idn, str(datetime.now()))
	Timer(60, sendActivity).start()

sendActivity()


# def sendLivePhoto(): 
# 	while True:
# 		try:
# 			global counter_live
# 			global frame 
# 			if not counter_live%5==0:
# 				pass
# 			image = Image.fromarray(frame)
# 			imgByteArr = io.BytesIO()
# 			image.save(imgByteArr, format='jpeg')
# 			imgByteArr = imgByteArr.getvalue()
# 			jpg_as_text = "data:image/jpeg;base64,"
# 			jpg_as_text += str(base64.b64encode(imgByteArr))[2:-1]
# 			r = requests.post("http://localhost:8000/api/live/"+device_idn+"/",
# 					headers=header, 
# 					data={'photo':jpg_as_text})
# 			counter_live +=1
# 			print(r.text)
# 			if counter_live>200:
# 				counter_live = 0
# 			break
# 		except:
# 			time.sleep(20)
# 			pass

# def sendLive():
# 	while True:
# 		try:
# 			global counter_live_first
# 			if counter_live_first == 0:
# 				counter_live_first = 1
# 				break
# 			r = requests.get("http://localhost:8000/api/live/"+device_idn+"/check/",
# 					headers=header)
# 			json_data = json.loads(r.text)
# 			if json_data['success']:
# 				sendLivePhoto()
# 			break
# 		except:
# 			time.sleep(20)
# 			pass
# 	Timer(3, sendLive).start()
# counter_live_first = 0
# sendLive()

# for i in range(5):
# 	GPIO.output(16, GPIO.HIGH)
# 	GPIO.output(21, GPIO.HIGH)
# 	GPIO.output(12, GPIO.HIGH)
# 	time.sleep(0.2)
# 	GPIO.output(12, GPIO.LOW)
# 	GPIO.output(16, GPIO.LOW)
# 	GPIO.output(21, GPIO.LOW)
# 	time.sleep(0.2)

# camera = picamera.PiCamera()
# camera.resolution = (960, 720)
# frame = np.empty((720,960,3),dtype=np.uint8)
cap = cv2.VideoCapture(0)
while True:
	# try:
		# camera.capture(frame, format="rgb", use_video_port=True)
		ret, frame = cap.read()
		cv2.imshow('frame',frame)
		
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = face_cascade.detectMultiScale(gray, 1.3, 5)
		faces = list(faces)
		if faces:
			# GPIO.output(16, GPIO.HIGH)
			for (x,y,w,h) in faces:
				
				face_loc = list([tuple(np.array([y, x+w, y+h, x]).tolist())])
				face_encoding = face_recognition.face_encodings(frame, face_loc)
				matches = face_recognition.face_distance(known_face_encodings, face_encoding[0])
				name_index = np.argmin(matches)
				# GPIO.output(16, GPIO..LOW)
				if (matches[name_index]<0.5):
					if known_face_pk[name_index] not in sended_face_pk:
						sended_face_pk.append(known_face_pk[name_index])
						t1 = Thread(target=sendPK, args=(name_index, frame))
						t1.start()
						Timer(600, refreshSendedList, args=[known_face_pk[name_index]]).start()
				else:
					
					if unknown_face_encodings:
						matches = face_recognition.face_distance(np.array(unknown_face_encodings), face_encoding)
						name_index = np.argmin(matches)
						if (matches[name_index]<0.5):
							continue
						else: 
							t2 = Thread(target=sendUnknown, args=(name_index, frame))
							t2.start()
							unknown_face_encodings.append(face_encoding)
							Timer(600, refreshUnknownList, args=[face_encoding]).start()
					else: 
						t2 = Thread(target=sendUnknown, args=(name_index, frame))
						t2.start()
						unknown_face_encodings.append(face_encoding)
						Timer(600, refreshUnknownList, args=[face_encoding]).start()
		Movement_B = False
		gray = cv2.GaussianBlur(gray, (21, 21), 0)
		if counter_motion_first == 0:
			firstFrame = gray
			counter_motion_first = 1
		if counter_motion == 20:
			firstFrame = gray
			counter_motion = 0
		frameDelta = cv2.absdiff(firstFrame, gray)
		thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
		thresh = cv2.dilate(thresh, None, iterations=2)
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
								cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		for c in cnts:
			if cv2.contourArea(c) < 500:
				continue
			Movement_B = True
		if Movement_B:
			if datetime.now() > (movement_time+timedelta(seconds = 10)):
				t3 = Thread(target=sendMovement, args=(str(datetime.now()),str(datetime.now())))
				t3.start()
				movement_time = datetime.now()
		counter_motion +=1
		# GPIO.output(16, GPIO.LOW)
		#cv2.imshow('frame',frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
cap.release()
cv2.destroyAllWindows()

	# except KeyboardInterrupt:
	# 	GPIO.output(21, GPIO.LOW)
	# 	GPIO.output(12, GPIO.LOW)
	# 	GPIO.output(16, GPIO.LOW)
	# 	break
	# except:
	# 	pass	
