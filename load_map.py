import pygame as pg
import sys
import numpy as np
import sys
from PIL import Image
import map as m

class load_map:
    
    def __init__(self, screen, image, x, y):
        self.image = image
        self.screen = screen
        self.x = x
        self.y = y
        self.width = 300
        self.length = 300
        self.rect = pg.Rect(x, y, self.width, self.length)
        self.active = False
    def draw(self):
        draw_map = pg.image.load(self.image)
        draw_map = pg.transform.scale(draw_map, (self.width, self.length))
        if self.active:
            pg.draw.rect(self.screen, 'Yellow', (self.x - 3, self.y - 3, self.width + 6, self.length + 6), 3)
        self.screen.blit(draw_map, (self.x,self.y))

        
            