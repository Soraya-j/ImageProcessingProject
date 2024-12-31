import cv2
import mediapipe.python.solutions.hands as mp_hands
#import mediapipe.python.solutions.drawing_utils as drawing
#import mediapipe.python.solutions.drawing_styles as drawing_styles

hands = mp_hands.Hands(static_image_mode=False,max_num_hands=2,min_detection_confidence=0.5)
       
def capture_video():        
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
    while (True):
        ret, frame = cam.read()
        flip_frame = cv2.flip(frame,1) 

        img_rgb = cv2.cvtColor(flip_frame, cv2.COLOR_BGR2RGB)
        hands_detected = hands.process(img_rgb)

        img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        if hands_detected.multi_hand_landmarks:
            print('Une main est detectee')
        else : 
            print('Aucune main detectee')
            # for hand_landmarks in hands_detected.multi_hand_landmarks:
            #     drawing.draw_landmarks(img_rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS, drawing_styles.get_default_hand_landmarks_style(), drawing_styles.get_default_hand_connections_style())
        cv2.imshow('Detected',img_rgb)
        if cv2.waitKey(5) == 27: # Quit with escape key (la touche echap)
            break
    cv2.destroyAllWindows()
    cam.release()

capture_video()