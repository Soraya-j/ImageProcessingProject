import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Game")

class Game:
    def __init__(self):
        self.player = Player()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # player lives
        self.health = 3
        self.speed = 10
        raven = pygame.image.load("Raven.png")
        self.raven = pygame.transform.smoothscale(raven, (80,80))
        self.rect = self.raven.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        

    def update(self):
        # # Get the current key state
        keys = pygame.key.get_pressed()

        # Move the player
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

game = Game()
continuer = True

while continuer:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            continuer = False
            pygame.quit()
    
    screen.blit(game.player.raven, game.player.rect)
    pygame.display.flip()
