import cv2
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as drawing
import pygame
import numpy as np
import random

hands = mp_hands.Hands(static_image_mode=False,max_num_hands=2,min_detection_confidence=0.5)
screen_width = 1200
screen_height = 700
prev_x = None
prev_y = None
direction = None
dir_list = ['left', 'right', 'up', 'down']
dir = random.choice(dir_list)
i = 0

pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game with hand detection")

class Game:
    def __init__(self):
        self.all_players = pygame.sprite.Group()
        self.player = Player(self)
        self.all_players.add(self.player)
        self.all_monsters = pygame.sprite.Group()
        self.pressed = {}
        self.spawn_monster()
    
    def check_collision(self, sprite, group):
        return pygame.sprite.spritecollide(sprite, group, False, pygame.sprite.collide_mask)

    def spawn_monster(self):
        monster = Monster(self)
        self.all_monsters.add(monster)

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        # player lives
        self.health = 90
        self.max_health = 90
        self.speed = 20
        image = pygame.image.load("Raven.png")
        self.image = pygame.transform.smoothscale(image, (80,80))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.all_power = pygame.sprite.Group()
    
    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.game.all_players.remove(self)

    def update_health_bar(self, surface):
        bar_color = (111,210,46)
        back_bar_color = (60,63,60)
        bar_position = [self.rect.x, self.rect.y - 20, self.health, 5]
        back_bar_position = [self.rect.x, self.rect.y - 20, self.max_health, 5]
        pygame.draw.rect(surface, back_bar_color, back_bar_position)
        pygame.draw.rect(surface, bar_color, bar_position)
    
    def power(self):
        power = SuperPower(self)
        self.all_power.add(power)

    def move(self, direction):
        if direction == 'left' and self.rect.x > 0:
            if not self.game.check_collision(self, self.game.all_monsters):
                self.rect.x -= self.speed
        elif direction == 'right' and self.rect.x + self.rect.width < screen_width:
            if not self.game.check_collision(self, self.game.all_monsters):
                self.rect.x += self.speed
        elif direction == 'up' and self.rect.y > 0:
            if not self.game.check_collision(self, self.game.all_monsters):
                self.rect.y -= self.speed
        elif direction == 'down' and self.rect.y + self.rect.height < screen_height:
            if not self.game.check_collision(self, self.game.all_monsters):
                self.rect.y += self.speed

class SuperPower(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.speed = 50
        self.player = player
        image = pygame.image.load("fire.png")
        self.image = pygame.transform.smoothscale(image, (30,30))
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.x
        self.rect.y = player.rect.y

    def move(self): 
        self.rect.x += self.speed
        for monster in self.player.game.check_collision(self, self.player.game.all_monsters):
            self.player.all_power.remove(self)
            monster.damage(30)
        if self.rect.x > screen_width:
            self.player.all_power.remove(self)

class Monster(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        image = pygame.image.load('monster.png')
        self.image = pygame.transform.smoothscale(image,(60,60))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width)
        self.rect.y = random.randint(0, screen_height)
        self.speed = 15
        self.health = 60
        self.max_health = 60
    
    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            #Je pourrais en faire apparaitre un autre à la place de le supprimer
            self.game.all_monsters.remove(self)
    
    def update_health_bar(self, surface):
        bar_color = (111,210,46)
        back_bar_color = (60,63,60)
        bar_position = [self.rect.x, self.rect.y - 20, self.health, 5]
        back_bar_position = [self.rect.x, self.rect.y - 20, self.max_health, 5]
        pygame.draw.rect(surface, back_bar_color, back_bar_position)
        pygame.draw.rect(surface, bar_color, bar_position)
    
    def move(self):
        global i, dir, dir_list
        if i < 10 :
            i = i + 1
        else:
            dir = random.choice(dir_list)
            i = 0
            print('dir : ', dir)
        if self.game.check_collision(self, self.game.all_players):
            self.game.player.damage(10)
        if dir == 'left' and self.rect.x > 0:
            self.rect.x  -= self.speed
        elif dir == 'right' and self.rect.x + self.rect.width < screen_width:
            self.rect.x += self.speed
        elif dir == 'down' and self.rect.y + self.rect.height < screen_height:
            self.rect.y  += self.speed
        elif dir == 'up' and self.rect.y > 0:
            self.rect.y -= self.speed
        else :
            dir = random.choice(dir_list)

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

    def detect_gesture_left(hand_landmarks):
        finger_tips = [8, 12, 16, 20]  
        finger_mcp = [6, 10, 14, 18]    
        
        fingers_up = []
        for tip, mcp in zip(finger_tips, finger_mcp):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[mcp].y:
                fingers_up.append(True)  
            else:
                fingers_up.append(False) 
                
        if not fingers_up[0] and all(fingers_up[1:]):
            raven = pygame.image.load("Attack.png")
            game.player.image = pygame.transform.smoothscale(raven, (80,80))
            print('Super Power')
            game.player.power()
        elif not any(fingers_up):
            print('Break')
        else :
            raven = pygame.image.load("Raven.png")
            game.player.image = pygame.transform.smoothscale(raven, (80,80))
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

    while running:
        ret, frame = cam.read()
        flip_frame = cv2.flip(frame, 1)
        img_brg = cv2.cvtColor(flip_frame, cv2.COLOR_BGR2RGB)
        img_rgb = detect_hand(img_brg)
        
        pg_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(np.rot90(pg_frame))

        screen.blit(frame_surface, (0, 0))
        if game.player.health > 0:
            screen.blit(game.player.image, game.player.rect)
            game.player.update_health_bar(screen)
        else :
            myfont = pygame.font.SysFont("Comic Sans MS", 30)
            label = myfont.render("Game Over", 1, (255, 0, 0))
            screen.blit(label, (500, 350))

        for power in game.player.all_power:
            power.move()
        for monster in game.all_monsters:
            monster.move()
            monster.update_health_bar(screen)

        game.player.all_power.draw(screen)
        game.all_monsters.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    cam.release()
    pygame.quit()

if __name__ == "__main__":
    main()