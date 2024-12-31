import pygame

pygame.init()
x = 800
y = 600
screen = pygame.display.set_mode((x, y))
pygame.display.set_caption("Game")

class Game:
    def __init__(self):
        self.player = Player()
        self.pressed = {}

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # player lives
        self.health = 3
        self.speed = 1
        raven = pygame.image.load("Raven.png")
        self.raven = pygame.transform.smoothscale(raven, (80,80))
        self.rect = self.raven.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        
    def move_left(self):
        self.rect.x -= self.speed
    def move_right(self):
        self.rect.x += self.speed
    def move_up(self):
        self.rect.y -= self.speed
    def move_down(self):
        self.rect.y += self.speed

game = Game()
continuer = True

while continuer:
    screen.fill((0, 0, 0))
    screen.blit(game.player.raven, game.player.rect)
    
    if game.pressed.get(pygame.K_RIGHT) and game.player.rect.x + game.player.rect.width < x :
        game.player.move_right()
    elif game.pressed.get(pygame.K_LEFT) and game.player.rect.x > 0:
        game.player.move_left()
    elif game.pressed.get(pygame.K_UP) and game.player.rect.y > 0 :
        game.player.move_up()
    elif game.pressed.get(pygame.K_DOWN) and game.player.rect.y + game.player.rect.height < y:
        game.player.move_down()


    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continuer = False
        elif event.type == pygame.KEYDOWN:
            game.pressed[event.key] = True
        elif event.type == pygame.KEYUP:
            game.pressed[event.key] = False

pygame.quit()
    
