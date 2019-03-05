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


test = 0
angle = get_rotate()
angle = 45
img = pygame.transform.rotate(ori_img[index], angle)
location = get_location()

print('Test ' + str(test) + ': ' + str(angle) + ', ' + str(location))
test += 1

while True:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_q:
                sys.exit()
            if event.key == K_r:
                # angle = get_rotate()
                angle += 90
                print('Test ' + str(test) + ': ' + str(angle) + ', ' + str(location))
                test += 1
                img = pygame.transform.rotate(ori_img[index], angle)
                location = get_location()
            if event.key == K_c:
                index = (index + 1) % 2
                img = pygame.transform.rotate(ori_img[index], angle)
    sur.fill((255, 255, 255))
    sur.blit(img, location)

    pygame.display.flip()
