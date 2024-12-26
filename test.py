import cv2
        
def capture_video():        
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while (True):
        ret, frame = cam.read()
        flip_frame = cv2.flip(frame,1) 
        cv2.imshow('Detected',flip_frame)
        if cv2.waitKey(5) == 27: # Quit with escape key (la touche echap)
            break
    cv2.destroyAllWindows()
    cam.release()

capture_video()