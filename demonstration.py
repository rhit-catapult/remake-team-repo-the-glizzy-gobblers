import pygame as pg
import numpy as np
import sys
import math
from PIL import Image 

def main():
    pg.init()
    screen = pg.display.set_mode((800,600)) # size
    running = True # while loop variable
    clock = pg.time.Clock()
    clock.tick(60)

    hres = 180 #horizontal resolution
    halfvres = 150 #vertical resolution/2
    scaling = 60
    mod = hres/scaling #scaling factor (fov set to 60)
    posx, posy, rot = 26.926, 17.938, 1.5 * np.pi #starting position and rotation angle
    moving_forward = False
    moving_backwards = False
    frame = np.random.uniform(0,1, (hres, halfvres*2, 3)) # 2d array that stores the image
    kart = pg.surfarray.array3d(pg.image.load('MarioKart2.png')) # import map
    sky = pg.image.load('skybox.jpg')
    sky = pg.surfarray.array3d(pg.transform.scale(sky, (360, halfvres*2)))/255
    ns = halfvres/((halfvres+0.1-np.linspace(0, halfvres, halfvres)))# depth used in calculating warp 
    
    base_max_speed = 0.006
    base_accel = 0.00005
    base_drift_speed = 0.0015
    min_speed = 0
    current_speed = 0
    backwards_speed = 0
    drift_time = 0
    drift_boosted = False
    DRIFT_BOOST_MS = 3000
    
    while running: # game loop begins
        dt = clock.tick(60)
        for event in pg.event.get(): # detect exiting loop: escape works to close
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

        keys = pg.key.get_pressed()
        drifting = keys[pg.K_LEFT] or keys[pg.K_RIGHT]
        if drifting and (moving_forward or current_speed > 0):
            drift_time += dt
        else:
            drift_time = 0
            drift_boosted = False
        if drift_time >= DRIFT_BOOST_MS:
            drift_boosted = True

        if drift_boosted:
            max_speed = base_max_speed * 1.3
            accel = base_accel * 1.5
            drift_speed = base_drift_speed * 1.5
        else:
            max_speed = base_max_speed
            accel = base_accel
            drift_speed = base_drift_speed

        frame = new_frame(posx, posy, rot, frame, sky, kart, hres, halfvres, mod, ns, scaling) # creates the frame (2d array representing colors)
        surf = pg.surfarray.make_surface(frame*255) # assigns color to a screen object based on a 2d array representing pixels
        surf = pg.transform.scale(surf, (800, 600)) # scales it to the size of the screen
        fps = int(clock.get_fps())
        
        pg.display.set_caption("Pycasting maze - FPS: " + str(fps) + " Speed: " + str(current_speed * 10000 - backwards_speed * 10000))
        
        screen.blit(surf, (0,0)) # draws the screen
        
        pg.display.update()
        
        # calculations on what speed should be sent to the movement method below
        if current_speed < max_speed and moving_forward:
            current_speed += accel
        if not moving_forward:
            if current_speed > min_speed: 
                current_speed -= accel * 2/3
                if(current_speed < accel * 3 and
                   current_speed > accel * -3):
                    current_speed = 0
        if backwards_speed < max_speed/3 and moving_backwards:
            backwards_speed += accel
        if not moving_backwards:
            if backwards_speed > min_speed: 
                backwards_speed -= accel
                if(backwards_speed < accel and
                   backwards_speed > accel * -1):
                    backwards_speed = 0
        
        # calculating movement below
        posx, posy, rot, moving_forward, moving_backwards = movement(posx, posy, rot, keys, dt, drift_speed, max_speed, current_speed, backwards_speed)

def movement(posx, posy, rot, keys, et, drift_speed, max_speed, current_speed, backwards_speed):
    x, y = (posx, posy)
    
    if color(posx, posy) not in (22, 23, 25, 29, 30): #if the car is not on track it should be slower
        current_speed *= 1/3
        backwards_speed *= 1/3
    x, y, rot, current_speed = drift(x, y, rot, keys, et, drift_speed, max_speed, current_speed)

    print(color(posx,posy))
   
      
    x, y = x + np.cos(rot)*current_speed*et,  y + np.sin(rot)*current_speed*et # changes position based on speed forwards
    
    x, y = x - np.cos(rot)*backwards_speed*et,  y - np.sin(rot)*backwards_speed*et
    
    posx, posy = (x, y) # for organization purposes

    # sends booleans determining if keys are held down
    # decides if the car should accelerate or not
    if not keys[pg.K_UP] and not keys[pg.K_DOWN]: 
        return posx, posy, rot, False, False
    elif not keys[pg.K_DOWN]:
        return posx, posy, rot, True, False
    elif not keys[pg.K_UP]:
        return posx, posy, rot, False, True
    return posx, posy, rot, True, True

def drift(x, y, rot, keys, et, drift_speed, max_speed, current_speed):

    side_x = math.sin(rot)
    side_y = math.cos(rot)
    drift_multiplier = 0.1
    if current_speed > 0.5 * max_speed:
        drift_multiplier = 0.12
    if current_speed > 0.7 * max_speed:
        drift_multiplier = 0.15
    if current_speed > 0.9 * max_speed:
        drift_multiplier = 0.18

    drift_slide = current_speed * drift_multiplier + drift_speed

    if keys[pg.K_LEFT]:
        rot = rot - 0.001*et
        x += side_x * drift_slide * et
        y += side_y * drift_slide * et
    if keys[pg.K_RIGHT]:
        rot = rot + 0.001*et
        x -= side_x * drift_slide * et
        y -= side_y * drift_slide * et
    return x, y, rot, current_speed

def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, depth, scaling):
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
            shade = 0.4 + 0.6*(np.linspace(0, halfvres, halfvres)/halfvres) # half of the vertical resolution: creates an array of evenly spaced tuples
            shade = np.dstack((shade, shade, shade)) # stacks the arrays to be 3d (3 2d arrays combine to be 3d)
            rot_i = rot + np.deg2rad(i/mod - scaling/2) # gets the end of the field of view, the 30 should be half of fov
            sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i/mod-scaling/2)) # creates warp based on trigonometry, pseudo 3d rendering
            frame[i][:halfvres] = sky[int(np.rad2deg(rot_i)%359)][:halfvres]/255 # the top half of the world should look like the sky
            xs, ys = posx+depth*cos/cos2, posy+depth*sin/cos2 # the position of the intended pixel 
            xxs, yys = (xs/30%1*1023).astype('int'), (ys/30%1*1023).astype('int') #position of the pixel/30 mod 1 time 1023 rounded 
            frame[i][2*halfvres-len(depth):2*halfvres] = shade*floor[np.flip(xxs),np.flip(yys)]/255 # puts the information into the correct place in frame
            
    return frame
def color(posx, posy):
    im = Image.open('MarioKart2.png') # Can be many different formats. imported from PIL
    pix = im.load() # loads the image. the image is 1024 by 1024, while posx and posy go up to 30, which means it needs converting
    return pix[round(1023 * (posx % 30)/30), round(1023 * (posy % 30)/30)] # returns color of position as a single int. uses 1023 to avoid out of bounds error

if __name__ == '__main__':
    main()
    pg.quit()
