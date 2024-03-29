import cv2
import mediapipe as mp
import numpy as np
from common import GESTURE_CATEGORIES, hand_landmark_to_model_input
import keras
from keras.models import load_model

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

MODEL_FILE_PATH = "mediapipe/8_gestures_best.h5"

PREDICTION_MIN_CONFIDENCE = 0.4

model = load_model(MODEL_FILE_PATH)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
with mp_hands.Hands(
		min_detection_confidence=0.5,
		min_tracking_confidence=0.5) as hands:
	while cap.isOpened():
		success, image = cap.read()
		if not success:
			print("Ignoring empty camera frame.")
			# If loading a video, use 'break' instead of 'continue'.
			continue

		# Flip the image horizontally for a later selfie-view display, and convert
		# the BGR image to RGB.
		image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
		# To improve performance, optionally mark the image as not writeable to
		# pass by reference.
		image.flags.writeable = False
		results = hands.process(image)

		# Draw the hand annotations on the image.
		image.flags.writeable = True
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
		if results.multi_hand_landmarks:
			for hand_landmarks in results.multi_hand_landmarks:
				mp_drawing.draw_landmarks(
						image,
						hand_landmarks,
						mp_hands.HAND_CONNECTIONS,
						mp_drawing_styles.get_default_hand_landmarks_style(),
						mp_drawing_styles.get_default_hand_connections_style())
			pred = model.predict([hand_landmark_to_model_input(results)])
			predictions_dict = dict(zip(GESTURE_CATEGORIES, pred[0]))
			if pred.max() > PREDICTION_MIN_CONFIDENCE:
				pred_idx = pred[0].argmax()
				cv2.rectangle(image, (10, 5), (150, 35), (255, 255, 255), thickness = -1)
				cv2.putText(image, GESTURE_CATEGORIES[pred_idx], (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
				#cv2.putText(image, str(predictions_dict), (15, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0))
			print(predictions_dict)

		cv2.imshow('MediaPipe Hands', image)
		if cv2.waitKey(5) & 0xFF == 27:
			break
cap.release()
cv2.destroyAllWindows()