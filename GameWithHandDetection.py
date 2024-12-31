import cv2
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as drawing
import pygame
import numpy as np

hands = mp_hands.Hands(static_image_mode=False,max_num_hands=2,min_detection_confidence=0.5)
screen_width = 1200
screen_height = 700
prev_x = None
prev_y = None
direction = None
pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game with hand detection")

class Game:
    def __init__(self):
        self.player = Player()
        self.pressed = {}

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # player lives
        self.health = 3
        self.speed = 20
        raven = pygame.image.load("Raven.png")
        self.raven = pygame.transform.smoothscale(raven, (80,80))
        self.rect = self.raven.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        
    def move(self, direction):
        if direction == 'left' and self.rect.x > 0:
            self.rect.x -= self.speed
        elif direction == 'right' and self.rect.x + self.rect.width < screen_width:
            self.rect.x += self.speed
        elif direction == 'up' and self.rect.y > 0:
            self.rect.y -= self.speed
        elif direction == 'down'and self.rect.y + self.rect.height < screen_height:
            self.rect.y += self.speed
        

def main():
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width + 150)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height + 100)

    game = Game()
    running = True
    def detect_gesture_right(hand_landmarks):
        global prev_x, prev_y 
        global direction

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
                
                if abs(dx) > abs(dy):
                    if dx > 20 :
                        direction = 'right'
                        print('move right')
                        
                    elif dx < -20 :
                        direction = 'left'
                        print('move left')
                else:  
                    if dy > 20 :
                        direction = 'down'  
                        print('move down')
                    elif dy < -20 :
                        direction = 'up'  
                        print('move up')
            game.player.move(direction)
            prev_x = x
            prev_y = y
            
        elif not any(fingers_up):  
            direction = None
            print("Close hand")
        else:
            print("unknow gesture")

    def detect_hand(frame):
        hands_detected = hands.process(frame)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if hands_detected.multi_hand_landmarks:
            for landmarks in hands_detected.multi_hand_landmarks:
                handedness = hands_detected.multi_handedness[hands_detected.multi_hand_landmarks.index(landmarks)].classification[0].label
                if handedness == "Left":  
                    print('LEFT hand detected')
                else :
                    print('RIGHT hand detected')
                    detect_gesture_right(landmarks)
        else : 
            print('No hands detected')

        return img_rgb

    while running:
        ret, frame = cam.read()
        flip_frame = cv2.flip(frame, 1)
        img_brg = cv2.cvtColor(flip_frame, cv2.COLOR_BGR2RGB)
        img_rgb = detect_hand(img_brg)
        
        pg_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(np.rot90(pg_frame))

        screen.blit(frame_surface, (0, 0))
        screen.blit(game.player.raven, game.player.rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game.pressed[event.key] = True
            elif event.type == pygame.KEYUP:
                game.pressed[event.key] = False

    cam.release()
    pygame.quit()

if __name__ == "__main__":
    main()