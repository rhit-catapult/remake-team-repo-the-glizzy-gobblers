import pygame as pg
import numpy as np
import sys
from PIL import Image
import math
import time 


def main():
    player_name, exit = menu()
    if exit:
        pg.quit()
    pg.init()
    screen = pg.display.set_mode((1200,900)) # size
    running = True # while loop variable
    clock = pg.time.Clock()

    hres = 300 #horizontal resolution
    halfvres = 512 #vertical resolution/2
    scaling = 60
    mod = hres/scaling #scaling factor (fov set to 60)
    posx, posy, rot = 26.926, 17.938, 1.5 * np.pi #starting position and rotation angle
    moving_forward = False
    moving_backwards = False
    frame = np.random.uniform(0,1, (hres, halfvres*2, 3)) # 2d array that stores the image
    kart = pg.surfarray.array3d(pg.image.load('MarioKart.png')) # import map
    sky = pg.image.load('skybox.jpg')
    sky = pg.surfarray.array3d(pg.transform.scale(sky, (360, halfvres*2)))
    ns = halfvres/((halfvres+0.1-np.linspace(0, halfvres, halfvres)))# depth used in calculating warp 
    lap_time = time.time()
    times_list = ['----','----','----']
    player_list = ['N/A','N/A','N/A']
    # speed variables below
    max_speed = 0.006
    turn_speed = max_speed * 0.75
    current_speed = 0
    backwards_speed = 0
    accel = 0.00002
    drift_speed = 0.0015
    rot_speed = [0, 0] # stores left speed at index 0 and right speed at index 1
    max_rot_speed = 0.0012
    offroad_speed = max_speed/3
    turning = [False, False]
    valid_lap = False
    while running: # game loop begins
        for event in pg.event.get(): # detect exiting loop: escape works to close
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
        
        frame = new_frame(posx, posy, rot, frame, sky, kart, hres, halfvres, mod, ns, scaling) # creates the frame (2d array representing colors)
        surf = pg.surfarray.make_surface(frame*255) # assigns color to a screen object based on a 2d array representing pixels
        surf = pg.transform.scale(surf, (1200, 900)) # scales it to the size of the screen
        fps = int(clock.get_fps())

        pg.display.set_caption("Pycasting maze - FPS: " + str(fps)) # debug info
        
        screen.blit(surf, (0,0)) # draws the screen

        # display all necessary screen info
        write(screen, 20 ,str(round((current_speed - backwards_speed) * 10000, 4)) + " MPH", 850, 700, 'White')
        write(screen, 20, "Lap time: " + str(round(time.time() - lap_time, 2)), 40, 40, 'White')
        write(screen, 20, 'Top Times:', 850, 40, 'White')
        
        for i in range(0,3):
            write(screen, 20, str(times_list[i]) + " - " + str(player_list[i]), 850, 80 + i * 40, 'White')
        
        
        
        pg.display.update()
        
        # calculations on what speeds should be sent to the movement method below

        if turning != [False, False]: # detects if turning to reduce speed while turning
            if max_speed <= turn_speed:
                max_speed = turn_speed
            else:
                max_speed -= accel/2

        else:
            max_speed = 0.006
        if current_speed < max_speed and moving_forward: # forward speed increase
            current_speed += accel
        
        if color(posx, posy) not in (22, 23, 28, 29, 30): #if the car is not on track it should be slower
            max_speed = offroad_speed
        

        if not moving_forward: # decceleration if nothing is held
            if current_speed > 0: 
                current_speed -= accel * 2/3
                if(current_speed < accel * 3 and
                   current_speed > accel * -3):
                    current_speed = 0

        if backwards_speed < max_speed/3 and moving_backwards: # backwards speed increase
            backwards_speed += accel/2
        if not moving_backwards: # decceleration if nothing is held
            if backwards_speed > 0: 
                backwards_speed -= accel
                if(backwards_speed < 0.001 and
                   backwards_speed > -0.001):
                    backwards_speed = 0

        if rot_speed[0] <= max_rot_speed and turning == [True, False]: # increment rotation speed assuming left key for cleaner fee
            rot_speed[0] += 0.00002
        else:
            if rot_speed[0] > 0: 
                rot_speed[0] -= 0.00008
                if(rot_speed[0] < 0.000025 and
                   rot_speed[0] > -1):
                    rot_speed[0] = 0
        if rot_speed[1] <= max_rot_speed and turning == [False, True]: # increment rotation speed assuming right key for cleaner fee
            rot_speed[1] += 0.00002
        else: 
            if rot_speed[1] > 0: 
                rot_speed[1] -= 0.00008
                if(rot_speed[1] < 0.000025 and
                   rot_speed[1] > -1):
                    rot_speed[1] = 0

        # catch all to make sure max variables are absolute
        if current_speed > max_speed:
            current_speed = max_speed
        if backwards_speed > max_speed/3:
            backwards_speed = max_speed/3

        # calculating movement below
        posx, posy, rot, moving_forward, moving_backwards, turning = movement(posx, posy, rot, pg.key.get_pressed(), clock.tick(), drift_speed, max_speed, current_speed, backwards_speed, rot_speed, max_rot_speed)

        # did we touch the finish line?
        if posx % 30 < 6 and posy % 30 > 15:
            valid_lap = True
        lap_time, times_list, player_list, valid_lap = (finish(color(posx, posy), lap_time, times_list, player_list, player_name, valid_lap))
    main()
    
def movement(posx, posy, rot, keys, et, drift_speed, max_speed, current_speed, backwards_speed, rot_speed, max_rot_speed):
    
    x, y = (posx, posy) # for organizational purposes
    
    # catch for higher speeds
    if rot_speed[0] > max_rot_speed:
        rot_speed[0] = max_rot_speed
    if rot_speed[1] > max_rot_speed:
        rot_speed[1] = max_rot_speed

    x, y, rot, current_speed, turning = drift(x, y, rot, keys, et, current_speed, rot_speed)

    x, y = x + np.cos(rot)*current_speed*et,  y + np.sin(rot)*current_speed*et # changes position based on speed forwards
    
    x, y = x - np.cos(rot)*backwards_speed*et,  y - np.sin(rot)*backwards_speed*et # changes position based on speed backwards
    
    posx, posy = (x, y) # for organization purposes

    # sends booleans determining if keys are held down
    # decides if the car should accelerate or not
    if not keys[pg.K_UP] and not keys[pg.K_DOWN]: 
        return posx, posy, rot, False, False, turning
    elif not keys[pg.K_DOWN]:
        return posx, posy, rot, True, False, turning
    elif not keys[pg.K_UP]:
        return posx, posy, rot, False, True, turning
    return posx, posy, rot, True, True, turning

def drift(x, y, rot, keys, et, current_speed, rot_speed):
    
    perp_x = math.sin(rot)
    perp_y = -math.cos(rot)

    drift_slide = current_speed * 0.35
    turning = []

    if keys[pg.K_LEFT]:
        x -= perp_x * drift_slide * 1000 * rot_speed[0] * et
        y -= perp_y * drift_slide * 1000 * rot_speed[0] * et
        turning.append(True)
    else:
        turning.append(False)

    if keys[pg.K_RIGHT]:
        x += perp_x * drift_slide * 1000 * rot_speed[1] * et
        y += perp_y * drift_slide * 1000 * rot_speed[1] * et
        turning.append(True)
    else:
        turning.append(False)

    rot = rot + rot_speed[1]*et
    rot = rot - rot_speed[0]*et

    return x, y, rot, current_speed, turning

def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, depth, scaling):
    
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

    im = Image.open('MarioKart.png') # Can be many different formats. imported from PIL
    pix = im.load() # loads the image. the image is 1024 by 1024, while posx and posy go up to 30, which means it needs converting
    return pix[round(1023 * (posx % 30)/30), round(1023 * (posy % 30)/30)] # returns color of position as a single int. uses 1023 to avoid out of bounds error

def finish(color_int, lap_time, times_list, player_list, player_name, valid_lap):

    if color_int in (30, 28): # color of the finish, can be changed
        if (time.time() - lap_time > 10): # just make sure it's not too short
            i = 0
            for x in times_list: # add to an array
                if  (x == '----' or time.time() - lap_time <= x) and valid_lap:
                    times_list.insert(i, round(time.time() - lap_time, 2))
                    player_list.insert(i, player_name)
                    break
                elif times_list.index(x) == len(times_list) - 1:
                    times_list.append(round(time.time() - lap_time, 2))
                    player_list.append(player_name)
                else:
                    i += 1

        return time.time(), times_list, player_list, False # returns current time before the epoch
    return lap_time, times_list, player_list, valid_lap # returns starting time in time before the epoch

def write(screen, size, text, x, y, color):

    font = pg.font.Font("8bit.ttf", size)
    caption = font.render(text, True, color)
    screen.blit(caption, (x,y))
    return screen

def menu():
    # mostly AI unfortunately
    pg.init()
    screen = pg.display.set_mode((1200, 900))
    pg.display.set_caption("Cart Race!")
    font = pg.font.Font('8bit.ttf', 30)

    input_rect = pg.Rect(380, 500, 440, 45)
    color_active = pg.Color("dodgerblue2")
    color_inactive = pg.Color("lightskyblue3")
    box_color = color_inactive

    user_text = ""
    active = False
    running = True
    exit = False

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
                exit = True

            if event.type == pg.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                    box_color = color_active
                else:
                    active = False
                    box_color = color_inactive

            if active:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE:
                        user_text = user_text[:-1]
                    elif event.key == pg.K_RETURN:
                        submitted_text = user_text
                        user_text = ''
                        return submitted_text, exit

                elif event.type == pg.TEXTINPUT:
                    user_text += event.text
    
        screen.fill((30, 30, 30))

        text_surface = font.render(user_text, True, (255, 255, 255))

        input_rect.w = max(440, text_surface.get_width() + 10) 
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 7))

        write(screen, 50, "Kart Race!", 375, 200, 'Red')
        write(screen, 30, "Name:", 380, 460, 'White')
        pg.draw.rect(screen, box_color, input_rect, 3)

        pg.display.flip()
    return submitted_text, exit


if __name__ == '__main__':
    main()
    pg.quit()
