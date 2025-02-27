import cv2
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as drawing
#import mediapipe.python.solutions.drawing_styles as drawing_styles

hands = mp_hands.Hands(static_image_mode=False,max_num_hands=2,min_detection_confidence=0.5)
screen_width = 1280
screen_height = 960
prev_x = None
prev_y = None

def detect_gesture_right(hand_landmarks):
    global prev_x, prev_y 
    finger_tips = [8, 12, 16, 20]  
    finger_mcp = [6, 10, 14, 18]    
    
    fingers_up = []
    for tip, mcp in zip(finger_tips, finger_mcp):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[mcp].y:
            fingers_up.append(True)  
        else:
            fingers_up.append(False)  

    if all(fingers_up):  
        print("Open hand")
        x, y = int(hand_landmarks.landmark[0].x * screen_width), int(hand_landmarks.landmark[0].y * screen_height)
        if prev_x is not None and prev_y is not None:
            dx = x - prev_x
            dy = y - prev_y
            print(dx, dy)

            if abs(dx) > abs(dy):
                if dx > 10:  
                    print('move right')
                elif dx < -10: 
                    print('move left')
            else:  
                if dy > 10:  
                    print('move down')
                elif dy < -10:  
                    print('move up')
        prev_x = x
        prev_y = y
        
    elif not any(fingers_up):  
        print("Close hand")
    else:
        print("unknow gesture")

def detect_gesture_left(hand_landmarks):
        finger_tips = [8, 12, 16, 20, 4]  
        finger_mcp = [6, 10, 14, 18, 3]    
        
        fingers_up = []
        for tip, mcp in zip(finger_tips, finger_mcp):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[mcp].y:
                fingers_up.append(True)  
            else:
                fingers_up.append(False) 
        print(fingers_up[:2], fingers_up[2:])       
        if not fingers_up[0] and all(fingers_up[1:]):
            print('Super Power')
        elif not any(fingers_up[:4]):
            print('Break')
        else :
            print('waiting')

def detect_hand(frame):
    hands_detected = hands.process(frame)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    if hands_detected.multi_hand_landmarks:
        for landmarks in hands_detected.multi_hand_landmarks:
            handedness = hands_detected.multi_handedness[hands_detected.multi_hand_landmarks.index(landmarks)].classification[0].label
            if handedness == "Left":  
                detect_gesture_left(landmarks)
                print('LEFT hand detected')
            else :
                print('RIGHT hand detected')
                detect_gesture_right(landmarks)
    else : 
        print('No hands detected')

    return img_rgb
        

def capture_video(width, height):        
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    while (True):
        ret, frame = cam.read()
        flip_frame = cv2.flip(frame,1) 
        img_bgr = cv2.cvtColor(flip_frame, cv2.COLOR_BGR2RGB)
        img_rgb = detect_hand(img_bgr)
            # for hand_landmarks in hands_detected.multi_hand_landmarks:
            #     drawing.draw_landmarks(img_rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS, drawing_styles.get_default_hand_landmarks_style(), drawing_styles.get_default_hand_connections_style())
        cv2.imshow('Detected',img_rgb)
        if cv2.waitKey(5) == 27: # Quit with escape key (la touche echap)
            break
    cv2.destroyAllWindows()
    cam.release()

capture_video(screen_width, screen_height)