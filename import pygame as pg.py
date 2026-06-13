import pygame as pg
import numpy as np
from numba import njit
import sys
from PIL import Image
import math


def main():
    pg.init()
    screen = pg.display.set_mode((800,600))
    running = True
    clock = pg.time.Clock()
    clock.tick(60)

    hres = 180 #horizontal resolution
    halfvres = 150 #vertical resolution/2

    mod = hres/60 #scaling factor (60° fov)
    posx, posy, rot = 0, 0, 0
    moving_forward = False
    moving_backwards = False
    frame = np.random.uniform(0,1, (hres, halfvres*2, 3))
    kart = pg.surfarray.array3d(pg.image.load('MarioKart.png'))
    sky = pg.image.load('skybox.jpg')
    sky = pg.surfarray.array3d(pg.transform.scale(sky, (360, halfvres*2)))/255
    ns = halfvres/((halfvres+0.1-np.linspace(0, halfvres, halfvres)))# depth
    
    max_speed = 0.01
    min_speed = 0
    current_speed = 0
    backwards_speed = 0
    drift_speed = 0.0015
    accel = 0.00005
    rot = 0



    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

        frame = new_frame(posx, posy, rot, frame, sky, kart, hres, halfvres, mod, ns)

        surf = pg.surfarray.make_surface(frame*255)
        surf = pg.transform.scale(surf, (800, 600))
        fps = int(clock.get_fps())
        
        pg.display.set_caption("Pycasting maze - FPS: " + str(fps) + " Speed: " + str(current_speed * 10000 - backwards_speed * 10000) + " MPH")
        
        screen.blit(surf, (0,0))
        
        pg.display.update()

        if current_speed < max_speed and moving_forward:
            current_speed += accel
        if not moving_forward:
            if current_speed > min_speed: 
                current_speed -= accel/4
                if(current_speed < accel and
                   current_speed > accel * -1):
                    current_speed = 0
        if backwards_speed < 0.002 and moving_backwards:
            backwards_speed += accel/4
        if not moving_backwards:
            if backwards_speed > min_speed: 
                backwards_speed -= accel
                if(backwards_speed < accel and
                   backwards_speed > accel * -1):
                    backwards_speed = 0
        posx, posy, rot, moving_forward, moving_backwards = movement(posx, posy, rot, pg.key.get_pressed(), clock.tick(), accel, max_speed, current_speed, backwards_speed, drift_speed)


def drifting(posx, posy, rot, keys, et, max_speed, accel, current_speed, backwards_speed, drift_speed):    
    x, y = (posx, posy)
    side_x = -math.sin(rot)
    side_y = math.cos(rot)
    drift_slide = current_speed * 0.1

    
    if current_speed > 0.5 * max_speed:
        accel -= 0.000025

    if current_speed > 0.7 * max_speed:
        drift_slide = current_speed * 0.25
        drift_speed += 0.0001
        accel -= 0.000035
    if current_speed > 0.9 * max_speed:
        drift_slide = current_speed * 0.4
        drift_speed += 0.00015
        accel -= 0.000045

        
def movement(posx, posy, rot, keys, et, max_speed, accel, current_speed, backwards_speed, drift_speed):    
    x, y = (posx, posy)
    


    if keys[pg.K_LEFT]:
        rot = rot - 0.001*et
    
    if keys[pg.K_RIGHT]:
        rot = rot + 0.001*et


    posx, posy = (x, y)

    x, y = x + np.cos(rot)*current_speed*et,  y + np.sin(rot)*current_speed*et
    x, y = x - np.cos(rot)*backwards_speed*et,  y - np.sin(rot)*backwards_speed*et
    
    posx, posy = (x, y)
    if not keys[pg.K_UP] and not keys[pg.K_DOWN]:
        return posx, posy, rot, False, False
    elif not keys[pg.K_DOWN]:
        return posx, posy, rot, True, False
    elif not keys[pg.K_UP]:
        return posx, posy, rot, False, True
    return posx, posy, rot, True, True


# @njit()
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, depth):
    # for i in range(hres):
    #     rot_i = rot + np.deg2rad(i/mod - 30)
    #     sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i/mod - 30))
    #     frame[i][:] = sky[int(np.rad2deg(rot_i)%359)][:]
    #     for j in range(halfvres):
    #         n = (halfvres/(halfvres-j))/cos2
    #         x, y = posx + cos*n, posy + sin*n
    #         xx, yy = int(x*2%1*99), int(y*2%1*99)

    #         shade = 0.2 + 0.8*(1-j/halfvres)

    #         # frame[i][halfvres*2-j-1] = shade*floor[xx][yy]
    #         frame[i][halfvres*2-j-1:2*halfvres] = shade*floor[np.flip(xx),np.flip(yy)]/255
    for i in range(hres):
            shade = 0.4 + 0.6*(np.linspace(0, halfvres, halfvres)/halfvres)
            shade = np.dstack((shade, shade, shade))
            rot_i = rot + np.deg2rad(i/mod - 30)
            sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i/mod-30))
            frame[i][:halfvres] = sky[int(np.rad2deg(rot_i)%360)][:halfvres]/255
            xs, ys = posx+depth*cos/cos2, posy+depth*sin/cos2
            xxs, yys = (xs/30%1*1023).astype('int'), (ys/30%1*1023).astype('int')
            frame[i][2*halfvres-len(depth):2*halfvres] = shade*floor[np.flip(xxs),np.flip(yys)]/255

    return frame
    
if __name__ == '__main__':
    main()
    pg.quit()
