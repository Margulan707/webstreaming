# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# import the necessary packages
from pyimagesearch.motion_detection import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2
import face_recognition
# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

face_encodings = []
# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0, resolution=(400, 300), framerate=1).start()
time.sleep(2.0)
margulan = [array([-0.0837641 ,  0.11511211,  0.02933423, -0.05834825, -0.08147891,        0.00602655, -0.12095874, -0.09488405,  0.12567891, -0.08148528,        0.20784083, -0.02369555, -0.24580893, -0.08205955, -0.04304276,        0.1581317 , -0.16193087, -0.146303  ,  0.00315377,  0.00185536,        0.08913954,  0.03906774, -0.04850782,  0.02270492, -0.07684278,       -0.3191753 , -0.03681897, -0.03616782, -0.04202789, -0.03593263,       -0.03255053,  0.08553062, -0.15601732,  0.01091965,  0.06816065,        0.15831657,  0.02198109,  0.03040396,  0.13709937,  0.04983601,       -0.230003  ,  0.03614018,  0.04057712,  0.21841478,  0.16255096,        0.06282556,  0.00497756, -0.0907829 ,  0.13275594, -0.18232982,        0.03096674,  0.22677268,  0.1597718 ,  0.02202979,  0.04227015,       -0.16046543, -0.03598528,  0.15088552, -0.13039233,  0.01357671,        0.06307071, -0.0626799 , -0.02323499, -0.13513821,  0.17124608,        0.07803162, -0.13868417, -0.16686833,  0.15492594, -0.09273249,       -0.16915174,  0.06518506, -0.17290384, -0.17748085, -0.2885133 ,        0.0277683 ,  0.34901369,  0.1125518 , -0.18241952,  0.0359807 ,        0.00670545, -0.01751127,  0.0331532 ,  0.10551079, -0.02253945,        0.00972355, -0.04758204, -0.03062819,  0.2147117 , -0.00117163,       -0.02241032,  0.14621992, -0.0450643 ,  0.12539493, -0.04648629,       -0.01410669, -0.01138926,  0.01477381, -0.15561673, -0.05944435,       -0.06954153, -0.06294758, -0.01953247,  0.1232525 , -0.17786501,        0.10445067,  0.00381743,  0.02946252, -0.03563542,  0.07907834,       -0.06575362,  0.00889499,  0.14013143, -0.22708619,  0.26057601,        0.19192992,  0.09637814,  0.07251853,  0.11425579,  0.04927793,        0.02587358, -0.05766675, -0.2105253 , -0.12310109,  0.05491357,       -0.05559611,  0.04640624,  0.01290911])]
temirlan = [array([-0.12856044,  0.15735161,  0.08240952, -0.0651532 , -0.07921558,       -0.03251234, -0.05334186, -0.09678037,  0.1081244 , -0.09472083,        0.33346733, -0.04174935, -0.26678732, -0.10986913, -0.05513319,        0.18462726, -0.13483724, -0.13110732, -0.09098004,  0.04381709,        0.09598634,  0.02156008, -0.00654753,  0.02073586, -0.0751069 ,       -0.37661278, -0.06854948, -0.03591737, -0.07171565, -0.07163045,       -0.03085672, -0.00422463, -0.18243754, -0.10732301,  0.01677791,        0.09048819, -0.06330357,  0.00680446,  0.18205062,  0.03418874,       -0.22597972,  0.15287858,  0.05317449,  0.30467793,  0.1922016 ,        0.1109111 , -0.00879447, -0.14527032,  0.09452185, -0.24261598,        0.07358078,  0.16692075,  0.15019734,  0.06434879,  0.01595972,       -0.12919791,  0.01172546,  0.10851005, -0.20568411,  0.00328518,        0.09006367, -0.0601288 , -0.01623532, -0.11023299,  0.16406927,        0.10355272, -0.14124572, -0.12919149,  0.06250069, -0.13757519,       -0.0940351 ,  0.04209307, -0.1656604 , -0.21152595, -0.3271853 ,        0.0876634 ,  0.38488212,  0.14433126, -0.22348586, -0.02871355,       -0.01787538,  0.02113814,  0.10750832,  0.08027541, -0.00782523,       -0.05763802, -0.08768311, -0.01148228,  0.16212721, -0.05621908,       -0.05293764,  0.22860472,  0.03129529,  0.08231859,  0.0270984 ,        0.03737979, -0.066245  ,  0.03347953, -0.16567196,  0.01996219,       -0.05715854, -0.03888872, -0.00603283,  0.06284341, -0.13415724,        0.1301249 ,  0.00406861,  0.02747032,  0.0023648 ,  0.055254  ,       -0.09703316, -0.09536848,  0.09575314, -0.20620099,  0.24724375,        0.22330023,  0.03653437,  0.10680263,  0.16661027,  0.06949524,       -0.01144994,  0.03344953, -0.176521  , -0.07825219,  0.08825494,        0.0121493 ,  0.13457192, -0.00058526])]
known_face_encodings = margulan.append(temirlan)

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

def detect_motion(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock

	# initialize the motion detector and the total number of frames
	# read thus far
	md = SingleMotionDetector(accumWeight=0.1)
	total = 0

	# loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		frame = vs.read()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)
		face_locations = face_recognition.face_locations(frame)

		face_landmarks_list = face_recognition.face_landmarks(frame, face_locations, 'large')
		# print(face_landmarks_list[0]['left_eye'])
		red = [0,0,255]
		if face_landmarks_list:
			for (x,y) in face_landmarks_list[0]['left_eye']:
				frame[y-2:y+2, x-2:x+2] = red
			for (x,y) in face_landmarks_list[0]['right_eye']:
				frame[y-2:y+2, x-2:x+2] = red
			for (x,y) in face_landmarks_list[0]['left_eyebrow']:
				frame[y-2:y+2, x-2:x+2] = red
			for (x,y) in face_landmarks_list[0]['right_eyebrow']:
				frame[y-2:y+2, x-2:x+2] = red
			for (x,y) in face_landmarks_list[0]['nose_tip']:
				frame[y-2:y+2, x-2:x+2] = red
			for (x,y) in face_landmarks_list[0]['nose_bridge']:
				frame[y-2:y+2, x-2:x+2] = red
			for (x,y) in face_landmarks_list[0]['top_lip']:
				frame[y-2:y+2, x-2:x+2] = red
			for (x,y) in face_landmarks_list[0]['bottom_lip']:
				frame[y-2:y+2, x-2:x+2] = red
			for (x,y) in face_landmarks_list[0]['chin']:
				frame[y-2:y+2, x-2:x+2] = red
		#grab the current timestamp and draw it on the frame
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		# if the total number of frames has reached a sufficient
		# number to construct a reasonable background model, then
		# continue to process the frame
		if total > frameCount:
			# detect motion in the image
			motion = md.detect(gray)

			# cehck to see if motion was found in the frame
			if motion is not None:
				# unpack the tuple and draw the box surrounding the
				# "motion area" on the output frame
				(thresh, (minX, minY, maxX, maxY)) = motion
				cv2.rectangle(frame, (minX, minY), (maxX, maxY),
					(0, 0, 255), 2)
		
		# update the background model and increment the total number
		# of frames read thus far
		md.update(gray)
		total += 1

		# acquire the lock, set the output frame, and release the
		# lock
		with lock:
			outputFrame = frame.copy()
		
def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())

	# start a thread that will perform motion detection
	t = threading.Thread(target=detect_motion, args=(
		args["frame_count"],))
	t.daemon = True
	t.start()

	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)

# release the video stream pointer
vs.stop()