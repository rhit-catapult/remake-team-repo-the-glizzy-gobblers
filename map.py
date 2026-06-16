import pygame as pg
import sys
from PIL import Image

class map:
    def __init__(self, image, times_list, player_list, track_colors, finish_colors, x, y, start_x, start_y, start_rot, valid_pos):
        self.image = image
        self.valid_lap = False
        self.times_list = times_list
        self.player_list = player_list
        self.threelap = []
        self.track_colors = track_colors
        self.finish_colors = finish_colors
        self.x = x
        self.y = y
        self.start_x = start_x
        self.start_y = start_y
        self.start_rot = start_rot
        self.valid_pos = valid_pos
        self.laps_run = 0

    def color(self, posx, posy):
        im = Image.open(self.image) # Can be many different formats. imported from PIL
        pix = im.load() # loads the image. the image is 1024 by 1024, while posx and posy go up to 30, which means it needs converting
        width, height = im.size
        return pix[round((width - 1) * (posx % 30)/30), round((height - 1) * (posy % 30)/30)] # returns color of position as a single int. uses 1023 to avoid out of bounds error