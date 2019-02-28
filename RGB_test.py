import pygame
from pygame.locals import *
import random
import sys
pygame.init()
sur = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
ori_img = [pygame.image.load('ori.png'), pygame.image.load('red.png')]
index = 0
img = ori_img[index]


def get_rotate():
    return random.randint(0, 360)


def get_location():
    return random.randint(0, 1320), random.randint(0, 480)

def get_color():
    return random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)

color = get_color()
print(color)

while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_q:
                sys.exit()
            if event.key == K_c:
                color = get_color()
                print(color)
    sur.fill(color)

    pygame.display.flip()
