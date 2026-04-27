import pygame
import random
import os

WIDTH, HEIGHT = 400, 600

def get_asset(name):
    if name.startswith("assets/"):
        return name
    return os.path.join("assets", name)

class Player(pygame.sprite.Sprite):
    def __init__(self, img_name="Player.png"):
        super().__init__()
        path = get_asset(img_name)
        self.image = pygame.transform.scale(pygame.image.load(path), (45, 90))
        self.rect = self.image.get_rect(center=(200, 520))
        self.shield = False

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= 7
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += 7

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        path = get_asset("Enemy.png")
        self.image = pygame.transform.scale(pygame.image.load(path), (45, 90))
        self.rect = self.image.get_rect(center=(random.randint(50, 350), -100))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.center = (random.randint(50, 350), -100)

class Collectible(pygame.sprite.Sprite):
    def __init__(self, itype, speed):
        super().__init__()
        self.type = itype
        path = get_asset(f"{itype}.png")
        img = pygame.image.load(path)
        size = (60, 35) if itype == 'oil' else (30, 30)
        self.image = pygame.transform.scale(img, size)
        self.rect = self.image.get_rect(center=(random.randint(30, 370), -100))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT: self.kill()