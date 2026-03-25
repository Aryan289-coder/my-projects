from facial_emotion_recognition import EmotionRecognition
import cv2

# for this line you need to change torch file and change cpu from none def load(f, map_location='cpu', pickle_module=pickle, **pickle_load_args): change this line 

emRec = EmotionRecognition(device='gpu')
cam = cv2.VideoCapture(0)

while True:
    success, frame = cam.read()
    frame = emRec.recognise_emotion(frame, return_type='BGR')
    cv.imshow('frame', frame)
    key = cv2.waitKey(1)
    if key == 27:
        break

cam.release()
cv2.destroyAllWindows()
