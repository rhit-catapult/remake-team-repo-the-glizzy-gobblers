import pygame as pg
import numpy as np
import sys
from PIL import Image
import math
import time 
import map as m
import load_map as lm

def main():

    map1 = m.map('MarioKart.png', ['----','----','----'], ['----','----','----'], ['N/A','N/A','N/A'], ['N/A','N/A','N/A'], [22, 23, 29], [28, 30], 1024, 1024, 26.926, 17.938, 1.5 * np.pi,[6,16])
    map2 = m.map('selfmade.png', ['----','----','----'], ['----','----','----'], ['N/A','N/A','N/A'], ['N/A','N/A','N/A'], [2], [3, 4], 1024, 1024, 26.926, 17.938, 1.5 * np.pi,[6,16])
    map3 = m.map('circle.png', ['----','----','----'], ['----','----','----'], ['N/A','N/A','N/A'], ['N/A','N/A','N/A'], [2], [3, 4], 1024, 1024, 26.926, 17.938, 1.5 * np.pi,[5,10])
    player_name, selected, exit = menu (map1, map2, map3)
    while selected == None:
        player_name, selected, exit = menu(map1, map2, map3)
   
    while(not exit):
        pg.init()
        screen = pg.display.set_mode((1200,800)) # size
        running = True # while loop variable
        clock = pg.time.Clock()
        brake_sound = pg.mixer.Sound("Car_brake.wav")
        car_sound = pg.mixer.Sound("Car_sound.wav")
        pg.mixer.music.load("MarioKartMusic.mp3")
        pg.mixer.music.play(-1)
    
        hres = 100 #horizontal resolution
        halfvres = 150 #vertical resolution/2
        scaling = 60
        mod = hres/scaling #scaling factor (fov set to 60)
        posx, posy, rot = selected.start_x, selected.start_y, selected.start_rot #starting position and rotation angle
        moving_forward = False
        moving_backwards = False
        frame = np.random.uniform(0,1, (hres, halfvres*2, 3)) # 2d array that stores the image
        kart = pg.surfarray.array3d(pg.image.load(selected.image)) # import map
        car = pg.image.load("Carbody.png")
        car_wheels = pg.image.load("Carwheels.png")
        sky = pg.image.load('skybox.jpg')
        sky = pg.surfarray.array3d(pg.transform.scale(sky, (360, halfvres*2)))
        ns = halfvres/((halfvres+0.1-np.linspace(0, halfvres, halfvres)))# depth used in calculating warp 
        lap_time = time.time()
        # speed variables below
        
        max_speed = 0.006
        static_max = 0.006
        
        current_speed = 0
        backwards_speed = 0
        accel = 0.00002

        if selected.image == map3.image:
            max_speed = 0.012
            accel = 0.00004
            static_max = 0.012

        turn_speed = max_speed * 0.75
        drift_speed = 0.0015
        rot_speed = [0, 0] # stores left speed at index 0 and right speed at index 1
        max_rot_speed = 0.0012
        offroad_speed = max_speed/3
        
        turning = [False, False]
        valid_lap = False
        check = time.time()
        while time.time() - check < 3:
            toprint = 3 - (time.time() - check)
            write(screen, 200, str(round(toprint) + 1), 500, 300, 'Black')
            write(screen, 200, str(round(toprint)), 500, 300, 'White')
            pg.display.update()
            
        lap_time = time.time()

        while running: # game loop begins
            
            
            

            # write()
            
            for event in pg.event.get(): # detect exiting loop: escape works to close
                if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_r:
                    posx, posy, rot = selected.start_x, selected.start_y, selected.start_rot
                    max_speed = 0.006
                    static_max = 0.006
                    
                    current_speed = 0
                    backwards_speed = 0
                    accel = 0.00002

                    if selected.image == map3.image:
                        max_speed = 0.012
                        accel = 0.00004
                        static_max = 0.012

                    turn_speed = max_speed * 0.75
                    drift_speed = 0.0015
                    rot_speed = [0, 0] # stores left speed at index 0 and right speed at index 1
                    max_rot_speed = 0.0012
                    offroad_speed = max_speed/3
                    
                    turning = [False, False]
                    valid_lap = False

                    lap_time = time.time()
                    selected.threelaps = []
                    selected.laps_run = 0
                    i = 0

            keys = pg.key.get_pressed()

            frame = new_frame(posx, posy, rot, frame, sky, kart, hres, halfvres, mod, ns, scaling, selected) # creates the frame (2d array representing colors)
            surf = pg.surfarray.make_surface(frame*255) # assigns color to a screen object based on a 2d array representing pixels
            surf = pg.transform.scale(surf, (1200, 900)) # scales it to the size of the screen
            fps = int(clock.get_fps())

            pg.display.set_caption("Pycasting maze - FPS: " + str(fps) + " Position: " + str(posx) + " " + str(posy)) # debug info
            
            screen.blit(surf, (0,0)) # draws the screen
        
            car_wheels = pg.transform.scale(car_wheels, (1000, 300))

            new_wheels = car_wheels

            # if keys[pg.K_UP] and current_speed <= 0.5 * max_speed:
            #     accel_sound.play()
            # else:
            #     accel_sound.stop()

            if current_speed - backwards_speed > 0 and not keys[pg.K_DOWN]:
                car_sound.play() 
                car_sound.set_volume(current_speed * 100 - backwards_speed * 100)
            else:
                car_sound.stop()
          
            if keys[pg.K_DOWN] and current_speed > 0:
                brake_sound.play()
                brake_sound.set_volume(current_speed * 200 - backwards_speed * 200)
            else:
                brake_sound.stop()

            
            if keys[pg.K_LEFT]:
                new_wheels = pg.transform.rotate(car_wheels, 5)
            elif keys[pg.K_RIGHT]:
                new_wheels = pg.transform.rotate(car_wheels, -5)
            elif keys[pg.K_LEFT] and current_speed > 0.5 * max_speed:
                new_wheels = pg.transform.rotate(car_wheels, 3)
            elif keys[pg.K_RIGHT] and current_speed > 0.5 * max_speed:
                new_wheels = pg.transform.rotate(car_wheels, -3)
            
            rotated_wheels = new_wheels.get_rect(center=car_wheels.get_rect(center=(600, 750)).center)
                
        
            screen.blit(new_wheels, rotated_wheels)

            car_x = (1200 - car.get_width()) // 2
            car_y = 860 - car.get_height()
            screen.blit(car, (car_x, car_y))

            
            # display all necessary screen info
            write(screen, 20 ,str(round((current_speed - backwards_speed) * 10000, 4)) + " MPH", 850, 700, 'White')
            write(screen, 20, "Lap " + str(min(selected.laps_run + 1, 3)) + "/3", 40,80, 'White')
            write(screen, 20, "Lap time: " + str(round(time.time() - lap_time, 2)), 40, 40, 'White')
            write(screen, 20, 'Fastest Laps:', 850, 40, 'White')
            
            
            for i in range(0,3):
                write(screen, 20, str(selected.times_list[i]) + " - " + str(selected.player_list[i]), 850, 80 + i * 40, 'White')
            i = 0
            for x in selected.threelaps:
                i+=1
                write(screen, 20, "Lap " + str(i) + " - " + str(x), 40, 80 + i * 40, 'White')
            
            if i == 3: 
                moving_forward = False
                moving_backwards = False
                accel = accel * 1.5
                if current_speed == 0:
                    selected.laps_run, selected.threelaps = ending(screen, selected, player_name)
                    break
    
            
            
            pg.display.update()
            
            # calculations on what speeds should be sent to the movement method below

            if turning != [False, False]: # detects if turning to reduce speed while turning
                if max_speed <= turn_speed:
                    max_speed = turn_speed
                else:
                    max_speed -= accel/2

            else:
                max_speed = static_max
            if current_speed < max_speed and moving_forward: # forward speed increase
                current_speed += accel
            print(selected.color(posx,posy))
            if selected.color(posx, posy) not in selected.track_colors: #if the car is not on track it should be slower
                if current_speed > offroad_speed:
                    current_speed -= accel * 4
                else:
                   pass
        
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
                rot_speed[0] += (0.00002 - current_speed/60000) # we can use calculations like these to make it harder while speeding up (change numbers)
            else:
                if rot_speed[0] > 0: 
                    rot_speed[0] -= 0.00008 
                    if(rot_speed[0] < 0.000025 and
                    rot_speed[0] > -1):
                        rot_speed[0] = 0
            if rot_speed[1] <= max_rot_speed and turning == [False, True]: # increment rotation speed assuming right key for cleaner fee
                rot_speed[1] += (0.00002 - current_speed/60000)
            else: 
                if rot_speed[1] > 0: 
                    rot_speed[1] -= 0.00008
                    if(rot_speed[1] < 0.000025 and
                    rot_speed[1] > -1):
                        rot_speed[1] = 0

            # catch all to make sure max variables are absolute
            if current_speed == 0 and backwards_speed == 0:
                rot_speed[0] = 0
                rot_speed[1] = 0

            if current_speed > max_speed:
                current_speed = max_speed
            if backwards_speed > max_speed/3:
                backwards_speed = max_speed/3

            # calculating movement below
            posx, posy, rot, moving_forward, moving_backwards, turning = movement(posx, posy, rot, pg.key.get_pressed(), clock.tick(), drift_speed, max_speed, current_speed, backwards_speed, rot_speed, max_rot_speed)

            # did we touch the finish line?
            if posx % 30 < selected.valid_pos[0] and posy % 30 > selected.valid_pos[1]:
                valid_lap = True
            lap_time, selected.times_list, selected.player_list, selected.laps_run, valid_lap = (finish(selected, selected.color(posx, posy), selected.finish_colors, lap_time, player_name, valid_lap))
            
        player_name, selected, exit = menu(map1, map2, map3)
    
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

def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, depth, scaling, map):
    
    for i in range(hres):
            shade = 0.4 + 0.6*(np.linspace(0, halfvres, halfvres)/halfvres) # half of the vertical resolution: creates an array of evenly spaced tuples
            shade = np.dstack((shade, shade, shade)) # stacks the arrays to be 3d (3 2d arrays combine to be 3d)
            rot_i = rot + np.deg2rad(i/mod - scaling/2) # gets the end of the field of view, the 30 should be half of fov
            sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i/mod-scaling/2)) # creates warp based on trigonometry, pseudo 3d rendering
            frame[i][:halfvres] = sky[int(np.rad2deg(rot_i)%359)][:halfvres]/255 # the top half of the world should look like the sky
            xs, ys = posx+depth*cos/cos2, posy+depth*sin/cos2 # the position of the intended pixel 
            xxs, yys = (xs/30%1*map.x - 1).astype('int'), (ys/30%1*map.y - 1).astype('int') #position of the pixel/30 mod 1 time map - 1 rounded 
            frame[i][2*halfvres-len(depth):2*halfvres] = shade*floor[np.flip(xxs),np.flip(yys)]/255 # puts the information into the correct place in frame
            
    return frame

def finish(selected, color_int, color_list, lap_time, player_name, valid_lap):
    lap_sound = pg.mixer.Sound("Lap_sound.wav")

    if color_int in color_list: # color of the finish, can be changed
        lap_sound.play()
        if (time.time() - lap_time > 2): # just make sure it's not too short
            i = 0
            for x in selected.times_list: # add to an array
        
                if  (x == '----' or time.time() - lap_time <= x) and valid_lap:
                    selected.times_list.insert(i, round(time.time() - lap_time, 2))
                    selected.threelaps.append(round(time.time() - lap_time, 2))
                    selected.laps_run += 1  
                    if player_name == '':
                        selected.player_list.insert(i, 'Anonymous')
                    else:
                        selected.player_list.insert(i, player_name)
                    break
                elif selected.times_list.index(x) == len(selected.times_list) - 1 and valid_lap:
                    selected.times_list.append(round(time.time() - lap_time, 2))
                    selected.player_list.append(player_name)
                    selected.laps_run += 1  
                else:
                    i += 1
              
            
        return time.time(), selected.times_list, selected.player_list, selected.laps_run, False # returns current time before the epoch
    return lap_time, selected.times_list, selected.player_list, selected.laps_run, valid_lap # returns starting time in time before the epoch

def write(screen, size, text, x, y, color):

    font = pg.font.Font("8bit.ttf", size)
    caption = font.render(text, True, color)
    screen.blit(caption, (x,y))
    return screen

def menu(map1, map2, map3):

    # mostly AI unfortunately
    pg.init()
    screen = pg.display.set_mode((1200, 900))
    pg.display.set_caption("Cart Race!")
    font = pg.font.Font('8bit.ttf', 30)

    input_rect = pg.Rect(380, 680, 440, 45)
    color_active = pg.Color("dodgerblue2")
    color_inactive = pg.Color("lightskyblue3")
    box_color = color_inactive

    load_mario = lm.load_map(screen, map1.image, 50, 300)
    load_selfmade = lm.load_map(screen, map2.image, 450, 300)
    load_circle = lm.load_map(screen, map3.image, 850, 300)
    map1.laps_run = 0
    map2.laps_run = 0
    map3.laps_run = 0

    user_text = ""
    active = False
    running = True
    exit = False

    while running:
        selected = None
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
                exit = True

            if event.type == pg.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                    box_color = color_active
                else:
                    if load_selfmade.rect.collidepoint(event.pos):
                        load_selfmade.active = True
                        load_mario.active = False
                        load_circle.active = False
                    elif load_mario.rect.collidepoint(event.pos):
                        load_mario.active = True
                        load_selfmade.active = False
                        load_circle.active = False
                    elif load_circle.rect.collidepoint(event.pos):
                        load_circle.active = True
                        load_selfmade.active = False
                        load_mario.active = False
                    else:
                        load_mario.active = False
                        load_selfmade.active = False
                        active = False
                        box_color = color_inactive
            # print(load_mario.active)
            # print(load_selfmade.active)
            if load_mario.active:
                selected = map1
                
            if load_selfmade.active:
                selected = map2

            if load_circle.active:
                selected = map3

            if active:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE:
                        user_text = user_text[:-1]
                    elif event.key == pg.K_RETURN:
                        submitted_text = user_text
                        user_text = ''
                        if not selected == None:
                            return submitted_text, selected, exit

                elif event.type == pg.TEXTINPUT:
                    user_text += event.text
    
        screen.fill((30, 30, 30))
        
        text_surface = font.render(user_text, True, (255, 255, 255))

        input_rect.w = max(440, text_surface.get_width() + 10)
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 7))

        load_mario.draw()
        load_selfmade.draw()
        load_circle.draw()

        write(screen, 50, "Cart Race!", 375, 120, 'Red')
        write(screen, 30, "Select a map: ", 50, 220, 'White')
        write(screen, 30, "Name:", 380, 640, 'White')
        pg.draw.rect(screen, box_color, input_rect, 3)

        pg.display.flip()
    return user_text, None, exit

def ending(screen, selected, player_name):
    i = 0

    for x in selected.threelaps_times_list: # add to an array
        if  x == '----' or round(sum(selected.threelaps)) <= x:
            selected.threelaps_times_list.insert(i, round(sum(selected.threelaps), 2))
            if player_name == '':
                selected.threelaps_player_list.insert(i, 'Anonymous')
            else:
                selected.threelaps_player_list.insert(i, player_name)
            break
        elif selected.threelaps_times_list.index(x) == len(selected.threelaps_times_list) - 1:
            selected.threelaps_times_list.append(round(sum(selected.threelaps), 2))
            selected.threelaps_player_list.append(player_name)
        else:
            i += 1

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

        screen.fill((30, 30, 30))

        write(screen, 20, "Lap " + str(min(selected.laps_run + 1, 3)) + "/3", 40,80, 'White')
        write(screen, 50, "Finish!", 380, 40, 'Red')
        write(screen, 30, "Map Leaderboard: ", 385, 300, 'White')
        write(screen, 20, 'Fastest Laps:', 850, 40, 'White')
        write(screen, 20, 'Press Escape to Exit', 750, 700, 'White')
    
        for x in range (0,3):
            write(screen, 20, str(selected.times_list[x]) + " - " + str(selected.player_list[x]), 850, 80 + (x) * 40, 'White')
            
        for x in range (0,11):
            if(x < len(selected.threelaps_times_list) and selected.threelaps_times_list[x] != '----'):
                write(screen, 20, str(x + 1) + '. ' + str(selected.threelaps_times_list[x]) + " - " + str(selected.threelaps_player_list[x]), 390, 340 + (x + 1) * 40, 'White')
        
        k = 0
        for x in selected.threelaps:
            k+=1
            write(screen, 20, "Lap " + str(k) + " - " + str(x), 40, 80 + k * 40, 'White')
        
        pg.display.update()
    return 0, []
    

if __name__ == '__main__':
    main()
    pg.quit()
