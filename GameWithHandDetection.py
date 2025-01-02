import cv2
import mediapipe.python.solutions.hands as mp_hands
import pygame
import numpy as np
import random

# use of the library mediapipe hand
hands = mp_hands.Hands(static_image_mode=False,             # for a video flux
                        max_num_hands=2,                    # max number of detected hands
                        min_detection_confidence=0.4)       # treshold for the detection confidence (between 0.0 and 1.0)
screen_width = 1200
screen_height = 700
prev_x = None
prev_y = None
direction = None
dir_list = ['left', 'right', 'up', 'down']
dir = random.choice(dir_list)
i = 0
box_x = [800,900,400,200]
box_y = [100,500,200,600]
lives_image = pygame.transform.smoothscale(pygame.image.load('image/heart.png'), (60,60))
key_image = pygame.transform.smoothscale(pygame.image.load('image/key.png'), (30,30))
door_image = pygame.transform.smoothscale(pygame.image.load('image/door.png'), (100, 100))

# pygame initialization
pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game with hand detection")

class Game:
    def __init__(self):
        # generation of these elements at game start
        self.all_players = pygame.sprite.Group()
        self.player = Player(self)
        self.all_players.add(self.player)
        self.all_monsters = pygame.sprite.Group()
        self.all_boxs = pygame.sprite.Group()
        self.all_items = pygame.sprite.Group()
        self.pressed = {}
        self.spawn_monster()
        self.spawn_item(box_x[0], box_y[0], lives_image, "lives")
        self.spawn_item(box_x[1], box_y[1], lives_image, "lives")        
        self.spawn_item(box_x[2], box_y[2], lives_image, "lives")
        self.spawn_item(box_x[3] + 15, box_y[3] + 10, key_image, "key")

        self.spawn_box(box_x[0], box_y[0], "with lives")
        self.spawn_box(box_x[1], box_y[1], "with lives")
        self.spawn_box(box_x[2], box_y[2], "with lives")
        self.spawn_box(box_x[3], box_y[3], "with key")
    
    def check_collision(self, sprite, group):
        return pygame.sprite.spritecollide(sprite, group, False, pygame.sprite.collide_mask)

    def spawn_monster(self):
        monster = Monster(self)
        self.all_monsters.add(monster)

    def spawn_box(self, x, y, box_type):
        box = Box(self, x, y, box_type)
        self.all_boxs.add(box)
    
    def spawn_item(self, x ,y, image, item_type):
        item = Items(self, x, y, image, item_type)
        self.all_items.add(item)

# class for the player
class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        # player lives
        self.health = 60
        self.max_health = 90
        self.speed = 15
        image = pygame.image.load("image/Raven.png")
        self.image = pygame.transform.smoothscale(image, (80,80))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.all_power = pygame.sprite.Group()
    
    def damage(self, amount):
        # decreases the player health of amount
        self.health -= amount
        if self.health <= 0:
            # remove the player if his healt is below or equal to zero
            self.game.all_players.remove(self)

    def update_health_bar(self, surface):
        # health bar to show the health status of the player
        bar_color = (111,210,46)
        back_bar_color = (60,63,60)
        bar_position = [self.rect.x,        # x position
                        self.rect.y - 20,   # y position
                        self.health,        # width (the health of the player)
                        5]                  # height
        # background of the health bar to show wath is the max
        back_bar_position = [self.rect.x, 
                            self.rect.y - 20, 
                            self.max_health,    # width (the health max of the player who never change)
                            5]
        # draw the two bar (rectangle)
        pygame.draw.rect(surface, back_bar_color, back_bar_position)
        pygame.draw.rect(surface, bar_color, bar_position)
    
    def power(self):
        # new instance of the SuperPower class
        power = SuperPower(self)
        self.all_power.add(power)

    def move(self, direction):
        # depend of the direction given in the function detect_gesture_right 
        # and if that doesn't mean going outside of the screen the player move
        if direction == 'left' and self.rect.x > 0:
                self.rect.x -= self.speed
        elif direction == 'right' and self.rect.x + self.rect.width < screen_width:
                self.rect.x += self.speed
        elif direction == 'up' and self.rect.y > 0:
                self.rect.y -= self.speed
        elif direction == 'down' and self.rect.y + self.rect.height < screen_height:
                self.rect.y += self.speed

    def broken(self):
        # call when all the fingers of the left hand are down
        # check if there is a collision between the player and a box
        collided_boxes = self.game.check_collision(self, self.game.all_boxs)
        for box in collided_boxes:
            box.damage(10) 
            # box has damage on his health (when it reaches zero, it is deleted)
            if box.type == "with key":
                # if its the box that hide the key who is broke
                # the door image appears
                self.game.spawn_item(600, 350, door_image, "door")
                

    def taken(self):
        # call when the 3 middle finger of the left hand are up 
        # check if there is a collision between the player and an item
        collided_items = self.game.check_collision(self, self.game.all_items)
        for item in collided_items:
            if item.type == "lives":
                # if item are lives they are remove and the player gains 10 health points
                self.game.all_items.remove(item)  
                self.health += 10
            elif item.type == "key" :
                # if the item is key his position become the player position
                item.rect.x = self.rect.x
                item.rect.y = self.rect.y  

    def release_key(self):
        collided_items = self.game.check_collision(self, self.game.all_items)
        for item in collided_items:
            if item.type == "door": 
                for item in collided_items: 
                    if item.type == "key":
                        self.game.all_players.remove(self)
                        self.health = -100              
                        print("FIN DU JEU")

# class for the Super power
class SuperPower(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.speed = 50
        self.player = player
        image = pygame.image.load("image/fire.png")
        self.image = pygame.transform.smoothscale(image, (30,30))
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.x
        self.rect.y = player.rect.y
        self.direction = direction

    def move(self): 
        # the power move into the direction of the player
        if self.direction == 'right':
            self.rect.x += self.speed
        elif self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed
        elif self.direction == 'up':
            self.rect.y -= self.speed

        # if the power collied a monster, the power is remove and the monster has damage
        for monster in self.player.game.check_collision(self, self.player.game.all_monsters):
            self.player.all_power.remove(self)
            monster.damage(20)
        if self.rect.x > screen_width or self.rect.x < 0 or self.rect.y > screen_height or self.rect.y < 0 :
            # if position of the power is beyond the screen it is delete
            self.player.all_power.remove(self)

class Box(pygame.sprite.Sprite):
    def __init__(self, game, x, y, box_type):
        super().__init__()
        self.game = game
        image = pygame.image.load('image/Box.png')
        self.image = pygame.transform.smoothscale(image, (60,60))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.healt = 20
        self.type = box_type
    
    def damage(self, amount):
        # is call when the player uses broken
        self.healt -= amount
        if self.healt <= 0:
            # the box is removed when his healt is below or equal to zero
            self.game.all_boxs.remove(self)

# class for the items (lives, key and door)
class Items(pygame.sprite.Sprite):
    def __init__(self, game, x, y, image, item_type):
        super().__init__()
        self.game = game
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = item_type

class Monster(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        image = pygame.image.load('image/monster.png')
        self.image = pygame.transform.smoothscale(image,(60,60))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width)
        self.rect.y = random.randint(0, screen_height)
        self.speed = 10
        self.health = 60
        self.max_health = 60
    
    def damage(self, amount):
        # call when the power of the player collide the monster
        self.health -= amount
        if self.health <= 0:
            # instead of deleting it we could make it reappear ailleur (improvement)
            self.game.all_monsters.remove(self)
    
    def update_health_bar(self, surface):
        # same function as the health bar of the player but with the health of the monster
        bar_color = (111,210,46)
        back_bar_color = (60,63,60)
        bar_position = [self.rect.x, self.rect.y - 20, self.health, 5]
        back_bar_position = [self.rect.x, self.rect.y - 20, self.max_health, 5]
        pygame.draw.rect(surface, back_bar_color, back_bar_position)
        pygame.draw.rect(surface, bar_color, bar_position)
    
    def move(self):
        # move the monster 
        # change the direction all 15 increment of i
        global i, dir, dir_list
        if i < 15 :
            i = i + 1
        else:
            # the direction is choose with random
            dir = random.choice(dir_list)
            i = 0
        if self.game.check_collision(self, self.game.all_players):
            # if the monster and the player collied the player has damage
            self.game.player.damage(5)
        # depending on the random direction chosen and if that doesn't mean going outside of the screen the monster move
        if dir == 'left' and self.rect.x > 0:
            self.rect.x  -= self.speed
        elif dir == 'right' and self.rect.x + self.rect.width < screen_width:
            self.rect.x += self.speed
        elif dir == 'down' and self.rect.y + self.rect.height < screen_height:
            self.rect.y  += self.speed
        elif dir == 'up' and self.rect.y > 0:
            self.rect.y -= self.speed
        else :
            # a new direction is chose if it can enter into the previous conditions
            # so the monster continue to move all the time
            dir = random.choice(dir_list)

def main():
    # initialization of the camera
    cam = cv2.VideoCapture(0)
    # define the width and heigth of the camera
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width + 150)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height + 100)

    game = Game()
    running = True

    def detect_gesture_right(hand_landmarks):
        global prev_x, prev_y 
        global direction

        # points for the index /middle /ring and pinky finger
        finger_tips = [8, 12, 16, 20]   # points for the tips of fingers
        finger_pip = [6, 10, 14, 18]    # points for the first finger joint
        
        fingers_up = []
        for tip, pip in zip(finger_tips, finger_pip):
            # this loop for look wich point is above the other
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                # if the position of the finger tip in y is higher than the position of the joint, this means that the finger is up
                # True is add to the list for every finger up
                fingers_up.append(True)  
            else:
                fingers_up.append(False)  

        if all(fingers_up):
            # if all the list == True, this means the hand is open
            print("Open hand")

            # the position of the hand on the screen is obtained in x and y
            x, y = int(hand_landmarks.landmark[0].x * screen_width), int(hand_landmarks.landmark[0].y * screen_height)
            if prev_x is not None and prev_y is not None:
                # the displacement delta is calculated between the previous position of the hand and the actual one
                dx = x - prev_x
                dy = y - prev_y
                
                # depending on the hand movement a direction is given for the player
                if dx > 30 :
                    direction = 'right'
                    print('move right')   
                elif dx < -30 :
                    direction = 'left'
                    print('move left')
                elif dy > 30 :
                    direction = 'down'  
                    print('move down')
                elif dy < -30 :
                    direction = 'up'  
                    print('move up')

            game.player.move(direction)
            prev_x = x
            prev_y = y
            
        elif not any(fingers_up):  
            # if all the finger are down (the hand is close); the direction = None the player is stop
            direction = None
            print("Close hand")
        else:
            print("unknow gesture")

    def detect_gesture_left(hand_landmarks):

        # points for the index /middle /ring /pinky and thumb finger
        finger_tips = [8, 12, 16, 20, 4]    # points for the tips of fingers
        finger_pip = [6, 10, 14, 18, 3]     # points for the first finger joint
        
        fingers_up = []
        for tip, pip in zip(finger_tips, finger_pip):
            # same loop as for the detect_gesture_right 
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                fingers_up.append(True)  
            else:
                fingers_up.append(False) 
                
        if not fingers_up[0] and all(fingers_up[1:]):
            # if the index finger is the only one down the player uses his super power
            # the image of the player is changed during "the attack" (until the position of the fingers changes)
            raven = pygame.image.load("image/Attack.png")
            game.player.image = pygame.transform.smoothscale(raven, (80,80))
            print('Super Power')
            game.player.power()
        elif not any(fingers_up[:4]) and fingers_up[4]:
            # if only the thumb is up 
            # the function release_key is called
            game.player.release_key()
            print('key release') 
        elif not any(fingers_up):
            # if the hand is close (all the fingers down) 
            # the function broken is called
            game.player.broken()
            print('Break')
        elif all(fingers_up[:3]) and not any(fingers_up[3:]):
            # if the index, middle, ring finger are up and the others are down
            # the function taken is called and the image of the player is changed
            game.player.taken()
            print('Item takes')
            raven = pygame.image.load('image/happyRaven.png')
            game.player.image = pygame.transform.smoothscale(raven, (80,80))
        else :
            # if there is no specific gesture the basic image of the player is restaured
            raven = pygame.image.load("image/Raven.png")
            game.player.image = pygame.transform.smoothscale(raven, (80,80))
            print('waiting')

    def detect_hand(frame):
        # detect if there is a hand and if it's the right or the left hand

        hands_detected = hands.process(frame)
        if hands_detected.multi_hand_landmarks:
            # we enter in this condition if hand are detect on the frame
            for landmarks in hands_detected.multi_hand_landmarks:
                handedness = hands_detected.multi_handedness[hands_detected.multi_hand_landmarks.index(landmarks)].classification[0].label
                if handedness == "Left":  
                    # if the left hand is detected we call the function who recognize the gestures for this hand
                    detect_gesture_left(landmarks)
                    print('LEFT hand detected')
                elif handedness == "Right":
                    # if the right hand is dected it's the right gesture function
                    print('RIGHT hand detected')
                    detect_gesture_right(landmarks)
        else : 
            print('No hands detected')

    while running:
        ret, frame = cam.read()
        # flip to see like a mirror
        flip_frame = cv2.flip(frame, 1)
        img_brg = cv2.cvtColor(flip_frame, cv2.COLOR_BGR2RGB)

        # call of the function detect_hand
        detect_hand(img_brg)
        
        # convert frame into pygame.Surface
        pg_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(np.rot90(pg_frame))

        # apply frame from the camera to the pygame background
        screen.blit(frame_surface, (0, 0))
        # draw items and boxs on top
        game.all_items.draw(screen)
        game.all_boxs.draw(screen)

        if game.player.health > 0:
            # if the player has still lives, it makes him and his health bar appear on the screen
            screen.blit(game.player.image, game.player.rect)
            game.player.update_health_bar(screen)
        elif game.player.health == -100:
            myfont = pygame.font.SysFont("Comic Sans MS", 150)
            label = myfont.render("You Win", 1, (200, 0, 200))
            screen.blit(label, (300, 200))
        else :
            myfont = pygame.font.SysFont("Comic Sans MS", 150)
            label = myfont.render("Game Over", 1, (255, 0, 0))
            screen.blit(label, (250, 200))

        for power in game.player.all_power:
            # call the function move for the SuperPower
            power.move()
        for monster in game.all_monsters:
            # call the function move and update_health_bar for the monster
            monster.move()
            monster.update_health_bar(screen)

        # draw power and monster on the screen
        game.player.all_power.draw(screen)
        game.all_monsters.draw(screen)
        
        # update of the screen
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                cam.release()   # release camera (stop capturing)
                pygame.quit()   # quit pygame and closing the window    

if __name__ == "__main__":
    main()