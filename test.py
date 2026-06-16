import pygame 
from PIL import Image

im = Image.open('Selfmade.png') # Can be many different formats. imported from PIL
pix = im.load() # loads the image. the image is 1024 by 1024, while posx and posy go up to 30, which means it needs converting
print(im.size)