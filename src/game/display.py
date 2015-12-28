import numpy
import math
import pygame
import pygame.gfxdraw
#import gradients
import random

class display(object):
    def __init__(self,init_scenario,game):
        # Initialize zoom options
        self.zoom_list = list()
        self.max_zoom_rate = 1000
        self.zoom_list.append("to_orbit")
        self.zoom_list.append("to_soi_earth")
        self.zoom_list.append("to_radius")
        self.zoom_list.append("to_altitude")
        self.zoom_list.append("hand_zoom_in")
        self.zoom_list.append("click_zoom_out")
        self.zoom_list.append("click_zoom_in")
        self.zoom_index = 0

        # Initialize pan options
        self.pan_list = list()
        self.pan_list.append("home")
        self.pan_list.append("vehicle")
        self.pan_list.append("hand_pan")
        self.pan_index = 0

        # Initialize viewing angle options
        self.viewing_angle_list = list()
        self.viewing_angle_list.append("home")
        self.viewing_angle_list.append("lvlh")
        self.viewing_angle_list.append("increment")
        self.viewing_angle_list.append("freeze")
        self.viewing_angle_index = 0

        # zoom scaling
        self.scale = 100
        self.prev_scale = 100

        self.original_center_x = 145
        self.original_center_y = 145
        self.center_x = self.original_center_x 
        self.center_y = self.original_center_y 
        self.center_r = (self.center_x, self.center_y)
        self.prev_center_x = self.center_y
        self.prev_center_y = self.center_x

        self.pan_click_1_pos_0 = 0
        self.pan_click_1_pos_1 = 0
        self.delta_pan_0 = 0.0
        self.delta_pan_1 = 0.0
        self.mouse_down_pan = 0

        # max slew of pan per cycle
        self.max_dist = 10000000000000000000

        self.r_trajectory = list()
        self.v_trajectory = list()

        self.original_viewing_angle = 1.5
        self.viewing_angle = self.original_viewing_angle

        if (init_scenario == "leo"):
             game.init_mode = True
             while not(game.mode_list[game.mode_index] == "earth_orbit"):
                 game.mode_index = game.mode_index + 1;
                 if game.mode_index >= len(game.mode_list):
                     game.mode_index = game.mode_index - len(game.mode_list)

        elif (init_scenario == "entry"):
             game.init_mode = True
             while not(game.mode_list[game.mode_index] == "earth_entry"):
                 game.mode_index = game.mode_index + 1;
                 if game.mode_index >= len(game.mode_list):
                     game.mode_index = game.mode_index - len(game.mode_list)

        if game.mode_list[game.mode_index] == "earth_orbit":
             self.zoom_index = 0
             self.pan_index = 0
             self.pan_angle_index = 0
        elif game.mode_list[game.mode_index] == "earth_entry":
             self.zoom_index = 5
             self.pan_index = 1
             self.viewing_angle_index = 1

    # update the display information
    def update(self,sim,screen,game,game_constants,earth,vehicle):

        # update viewing angle
        self.update_time_zoom(game,sim)

        # update angle viewing vehicle from
        self.update_viewing_angle(vehicle)

        # update zooming
        self.update_zoom(earth,vehicle)

        # update panning
        self.update_pan(vehicle)

        # compute location of bodies in the display space
        self.update_bodies(earth,vehicle)

        # Set the screen background
        screen.fill(game_constants.black)

        # draw the earth
        self.draw_earth(screen,earth,vehicle,game_constants)

        # draw the vehicle
        self.draw_vehicle(screen,vehicle,game_constants)

        # Do flight computer things
        self.draw_flight_computer(screen,game_constants)

        # show arrows to other things
        self.draw_arrow(screen,sim,game,vehicle,earth,game_constants)

        # draw text to the screen
        self.draw_text(screen,sim,game,vehicle,earth,game_constants)

    def update_time_zoom(self,game,sim):

        if game.dt_zoom_state == "zooming_out":
             if sim.dt >= 1.0:
                 game.dt_zoom_ratio = game.dt_zoom_ratio + 1
                 sim.dt = 1.0
             else:
                 sim.dt = sim.dt + 0.01

        if game.dt_zoom_state == "zooming_in":
             game.dt_zoom_ratio = game.dt_zoom_ratio - 1
             if (game.dt_zoom_ratio < 1):
                 game.dt_zoom_ratio = 1
                 sim.dt = sim.dt - 0.01
                 if sim.dt < 0.01:
                    sim.dt = 0.01

    def update_viewing_angle(self,vehicle):

        if self.viewing_angle_list[self.viewing_angle_index] == "home":
           self.viewing_angle = self.original_viewing_angle
        elif self.viewing_angle_list[self.viewing_angle_index] == "increment":
           self.viewing_angle = self.viewing_angle + 0.01
        elif self.viewing_angle_list[self.viewing_angle_index] == "freeze":
           self.viewing_angle = self.viewing_angle
        elif self.viewing_angle_list[self.viewing_angle_index] == "lvlh":
           self.viewing_angle = math.atan2(vehicle.r[0],vehicle.r[1]) + math.pi

    def update_pan(self,vehicle):

        r_display = numpy.array([0,0])
        if self.pan_list[self.pan_index] == "home":
           self.center_x_new = self.original_center_x
           self.center_y_new = self.original_center_y
        elif self.pan_list[self.pan_index] == "vehicle":
           r_display[0] = vehicle.r[0]*math.cos(self.viewing_angle) - vehicle.r[1]*math.sin(self.viewing_angle) 
           r_display[1] = vehicle.r[0]*math.sin(self.viewing_angle) + vehicle.r[1]*math.cos(self.viewing_angle) 
           self.center_x_new = -r_display[0]/self.scale + self.original_center_x
           self.center_y_new = -r_display[1]/self.scale + self.original_center_y
        elif self.pan_list[self.pan_index] == "hand_pan":
           self.center_x_new = self.prev_center_x + self.delta_pan_0
           self.center_y_new = self.prev_center_y + self.delta_pan_1
        length = math.sqrt((self.prev_center_x - self.center_x_new)**2 +
                      (self.prev_center_y - self.center_y_new)**2)
    
        if self.pan_list[self.pan_index] != "hand_pan":
            if (length > self.max_dist):
                self.center_x = self.prev_center_x + self.max_dist * (self.center_x_new - self.prev_center_x)/length
                self.center_y = self.prev_center_y + self.max_dist * (self.center_y_new - self.prev_center_y)/length 
            else:
                self.center_x = self.center_x_new
                self.center_y = self.center_y_new
        else:
            self.center_x = self.center_x_new
            self.center_y = self.center_y_new
    
        self.prev_center_x = self.center_x
        self.prev_center_y = self.center_y

        # zero out pan for next cycle
        self.delta_pan_0 = 0.0
        self.delta_pan_1 = 0.0

        # update center location
        self.center_r = numpy.array([self.center_x, self.center_y])


    def update_zoom(self,earth,vehicle):

        # throttle zoom scaling of the display such that
        # zooming is not too crazy
        #if (self.prev_scale-self.scale < 0) and \
        #   ( abs (self.prev_scale-self.scale) / self.scale > 0.01):
        #       self.scale = self.prev_scale + 0.01 * self.scale
        #elif (self.prev_scale-self.scale < 0) and \
        #   ( abs (self.prev_scale-self.scale) / self.scale > 0.1):
        #       self.scale = self.prev_scale - 0.05 * self.scale

        if self.zoom_list[self.zoom_index] == "to_orbit":
           if vehicle.ra < 0:
              self.scale = earth.r_soi/125
           elif vehicle.ra < earth.r_soi:
              self.scale = vehicle.ra/125
           else:
              self.scale = earth.r_soi/125
        elif self.zoom_list[self.zoom_index] == "to_soi_earth":
            self.scale = earth.r_soi/125
        elif self.zoom_list[self.zoom_index] == "to_radius":
            self.scale = numpy.linalg.norm(vehicle.r)/125
        elif self.zoom_list[self.zoom_index] == "to_altitude":
            #min_alt = 10000
            #if ((numpy.linalg.norm(vehicle.r)-earth.radius)/self.scale < min_alt):
            #    self.scale = (numpy.linalg.norm(vehicle.r)-earth.radius)/125
            #else:
            #    self.scale = 10000/125
            self.scale = max(1000,(numpy.linalg.norm(vehicle.r)-earth.radius))/125

        self.prev_scale = self.scale

    def update_bodies(self,earth,vehicle):

        vehicle.r_display[0] = vehicle.r[0]*math.cos(self.viewing_angle) - vehicle.r[1]*math.sin(self.viewing_angle) 
        vehicle.r_display[1] = vehicle.r[0]*math.sin(self.viewing_angle) + vehicle.r[1]*math.cos(self.viewing_angle) 
        vehicle.r_display = vehicle.r_display/self.scale + self.center_r

    def draw_earth(self,screen,earth,vehicle,game_constants):

        # draw the atmosphere
        # fancy atmosphere that is super slow during entry, so can't use it
        #scol   = (0,255,255,255)
        #ecol   = (20,0,30,255)
        #earth_atmos_radius = earth.radius+earth.atmosphere_height
        #screen.blit(gradients.radial(max(int((earth_atmos_radius)/self.scale),1), scol, ecol), 
        #            (self.center_r[0]-earth_atmos_radius/self.scale,self.center_r[1]-earth_atmos_radius/self.scale))
        #pygame.draw.ellipse(screen,line_color,box_dimensions,line_thickness)
        if self.scale > 250:
            for i in range(20):
                j = 20 - i
                self.draw_ellipse(screen,
                          self.center_r,
                          (earth.radius+25000*j/2)/self.scale,
                          (earth.radius+25000*j/2)/self.scale,
                          1,
                          [20,max(0,255-j*15),max(30,255-j*15)],
                          True,
                          [20,max(0,255-j*15),max(30,255-j*15)])

        # draw the earth centered at the display center
        if self.scale > 350:
           self.draw_ellipse(screen,
                          self.center_r,
                          earth.radius/self.scale,
                          earth.radius/self.scale,
                          1,
                          game_constants.blue,
                          True,
                          game_constants.dark_blue)
        else:
            # draw horizon
            self.draw_horizon(vehicle,earth,screen,game_constants)

        # draw surface features, starting with line for Prime Meridian
        if self.scale > 250:
            pygame.draw.line(screen,game_constants.green,self.center_r,
                        (earth.radius*math.cos(earth.angle+self.viewing_angle)/self.scale+self.center_r[0],
                        earth.radius*math.sin(earth.angle+self.viewing_angle)/self.scale+self.center_r[1]),
                        1)
            pygame.draw.line(screen,game_constants.red,self.center_r,
                        (earth.radius*math.cos(earth.angle+0.17+self.viewing_angle)/self.scale+self.center_r[0],
                        earth.radius*math.sin(earth.angle+0.17+self.viewing_angle)/self.scale+self.center_r[1]),
                        1)


    def draw_vehicle(self,screen,vehicle,game_constants):

        # vehicle length
        length = 100

        # create new surface with this width and height
        surf = pygame.Surface((length,length))
        test_surf = pygame.Surface((length,length))

        #set a color key for blitting
        surf.set_colorkey((0, 0, 0))

        #draw those two shapes to that surface
        sc_list = ((45,30),(55,30),(50,40))
        sc_list2 = ((45,40),(55,40),(55,60),(45,60))
        pygame.draw.polygon(surf,game_constants.grey,sc_list,0)
        pygame.draw.polygon(surf,game_constants.gold,sc_list2,0)

        # Vehicle update
        if (vehicle.thrusting):
            thrust_list = ((45,30),(55,30),(50,40))
            scol   = (255,255,255,255)
            ecol   = (20,0,30,255)
            plume_diameter = int(random.random()*5+10) 
            surf.set_clip(pygame.Rect(0,0,100,30))
            #surf.blit(gradients.radial(plume_diameter, scol, ecol), (50-plume_diameter, 30-plume_diameter)).clip
            surf.set_clip(None)
            #test_surf.blit(gradients.radial(plume_diameter, scol, ecol), (50-plume_diameter, 30-plume_diameter))
            #surf.blit(test_surf.set_clip(pygame.Rect(20,20,20,20)))

            pygame.draw.polygon(surf,game_constants.dark_red,thrust_list,0)

            #s = pygame.Surface((800, 600))
            #r = pygame.Rect(10, 10, 10, 10)
            #s.set_clip(r)
            #r.move_ip(10, 0)
            #s.set_clip(None)

        pygame.draw.line(surf,game_constants.blue, (50,50),(50,80),2)
        pygame.draw.line(surf,game_constants.green, (50,50),(80,50),2)
        pygame.draw.line(surf,game_constants.gold, (45,40),(40,30),3)
        #vel_mag = numpy.linalg.norm(vehicle.v) 
        #pygame.draw.line(surf,game_constants.magenta, (50,50),(50+30*vehicle.v[0]/vel_mag,50+30*vehicle.v[1]/vel_mag),2)

        #rotate surf by DEGREE amount degrees
        rotatedSurf = pygame.transform.rotate(surf, vehicle.attitude-self.viewing_angle*180/math.pi)

        #get the rect of the rotated surf and set it's center to the oldCenter
        rotRect = rotatedSurf.get_rect()
        rotRect.center = vehicle.r_display[0],vehicle.r_display[1]

        #draw rotatedSurf with the corrected rect so it gets put in the proper spot
        screen.blit(rotatedSurf, rotRect)

    def draw_ellipse(self,screen,r,smaja,smina,line_thickness,line_color,fill,fill_color=[0,0,0]):

        if (smina < 2*line_thickness):
            smaja = 2*line_thickness
            smina = 2*line_thickness
        box_dimensions = [r[0]-smaja,
                          r[1]-smina,
                          2*smaja,
                          2*smina]
        if (fill):
            pygame.draw.ellipse(screen,fill_color,box_dimensions,0)
        pygame.draw.ellipse(screen,line_color,box_dimensions,line_thickness)
        #pygame.gfxdraw.aaellipse(screen, box_dimensions, line_color)

    def draw_gradient_circle(self,screen,r,smaja,smina,line_thickness,line_color,fill,fill_color=[0,0,0]):

        if (smina < 2*line_thickness):
            smaja = 2*line_thickness
            smina = 2*line_thickness
        box_dimensions = [r[0]-smaja,
                          r[1]-smina,
                          2*smaja,
                          2*smina]
        if (fill):
            pygame.draw.ellipse(screen,fill_color,box_dimensions,0)
        pygame.draw.ellipse(screen,line_color,box_dimensions,line_thickness)

    def draw_flight_computer(self,screen,game_constants):

        pygame.draw.aalines(screen, game_constants.red, False, self.r_trajectory, 1)
        pygame.draw.aalines(screen, game_constants.magenta, False, self.v_trajectory, 1)

    def draw_arrow(self,screen,sim,game,vehicle,earth,game_constants):

        a = 1 
        # draw arrow to ares
        # draw velocity vector

    def draw_horizon(self,vehicle,earth,screen,game_constants):

            alt = ( numpy.linalg.norm(vehicle.r) -earth.radius)/self.scale
            horizon_display_y = alt+vehicle.r_display[1] 
            alt_horizon_2 = 2*(25000/2)/self.scale
            alt_horizon_3 = 2*(50000/2)/self.scale
            alt_horizon_4 = 2*(75000/2)/self.scale
            alt_horizon_5 = 2*(100000/2)/self.scale
            alt_horizon_6 = 2*(125000/2)/self.scale
            alt_horizon_7 = 2*(150000/2)/self.scale
            alt_horizon_8 = 2*(175000/2)/self.scale
            alt_horizon_9 = 2*(200000/2)/self.scale
            infinity = 10000

            j = 8
            sky = ( (infinity, -infinity), (-infinity, -infinity), (-infinity, infinity), (infinity, infinity) )
            pygame.draw.polygon(screen, [20,max(0,255-j*15),max(30,255-j*15)], sky, 0)

            j = 7
            sky = ( (infinity, horizon_display_y), (-infinity, horizon_display_y), (-infinity, horizon_display_y-alt_horizon_9), (-infinity, horizon_display_y - alt_horizon_9) )
            pygame.draw.polygon(screen, [20,max(0,255-j*15),max(30,255-j*15)], sky, 0)

            j = 6
            sky = ( (infinity, horizon_display_y), (-infinity, horizon_display_y), (-infinity, horizon_display_y-alt_horizon_8), (-infinity, horizon_display_y - alt_horizon_8) )
            pygame.draw.polygon(screen, [20,max(0,255-j*15),max(30,255-j*15)], sky, 0)

            j = 5
            sky = ( (infinity, horizon_display_y), (-infinity, horizon_display_y), (-infinity, horizon_display_y-alt_horizon_7), (-infinity, horizon_display_y - alt_horizon_7) )
            pygame.draw.polygon(screen, [20,max(0,255-j*15),max(30,255-j*15)], sky, 0)

            j = 4
            sky = ( (infinity, horizon_display_y), (-infinity, horizon_display_y), (-infinity, horizon_display_y-alt_horizon_6), (-infinity, horizon_display_y - alt_horizon_6) )
            pygame.draw.polygon(screen, [20,max(0,255-j*15),max(30,255-j*15)], sky, 0)

            j = 3
            sky = ( (infinity, horizon_display_y), (-infinity, horizon_display_y), (-infinity, horizon_display_y-alt_horizon_5), (-infinity, horizon_display_y - alt_horizon_5) )
            pygame.draw.polygon(screen, [20,max(0,255-j*15),max(30,255-j*15)], sky, 0)

            j = 2
            sky = ( (infinity, horizon_display_y), (-infinity, horizon_display_y), (-infinity, horizon_display_y-alt_horizon_4), (-infinity, horizon_display_y - alt_horizon_4) )
            pygame.draw.polygon(screen, [20,max(0,255-j*15),max(30,255-j*15)], sky, 0)

            j = 1
            sky = ( (infinity, horizon_display_y), (-infinity, horizon_display_y), (-infinity, horizon_display_y-alt_horizon_3), (-infinity, horizon_display_y - alt_horizon_3) )
            pygame.draw.polygon(screen, [20,max(0,255-j*15),max(30,255-j*15)], sky, 0)

            j = 0
            sky = ( (infinity, horizon_display_y), (-infinity, horizon_display_y), (-infinity, horizon_display_y-alt_horizon_2), (-infinity, horizon_display_y - alt_horizon_2) )
            pygame.draw.polygon(screen, [20,max(0,255-j*15),max(30,255-j*15)], sky, 0)

            #for i in range(360):
            mountain_longitude = 0
            mountain_height = 5000/self.scale
            mountain_location = ((mountain_longitude*earth.radius - vehicle.longitude *earth.radius) % 100000 - 100000/2) / self.scale + vehicle.r_display[0] 
            mountain_width = 5000/self.scale
            mountain_asymmetry = 0/self.scale
            mountain_1 = ( (mountain_location + mountain_width, horizon_display_y), (mountain_location-mountain_width, horizon_display_y), (mountain_location+mountain_asymmetry, horizon_display_y - mountain_height) )

            mountain_longitude = mountain_longitude + 0.01
            mountain_location = ((mountain_longitude*earth.radius - vehicle.longitude *earth.radius) % 100000 - 100000/2) / self.scale + vehicle.r_display[0] 
            mountain_height = 8000/self.scale
            mountain_width = 10000/self.scale
            mountain_asymmetry = 2000/self.scale
            mountain_2 = ( (mountain_location + mountain_width, horizon_display_y), (mountain_location-mountain_width, horizon_display_y), (mountain_location+mountain_asymmetry, horizon_display_y - mountain_height) )

            mountain_longitude = mountain_longitude + 0.01
            mountain_location = ((mountain_longitude*earth.radius - vehicle.longitude *earth.radius) % 100000 - 100000/2) / self.scale + vehicle.r_display[0] 
            mountain_height = 8000/self.scale
            mountain_width = 5000/self.scale
            mountain_asymmetry = -2000/self.scale
            mountain_3 = ( (mountain_location + mountain_width, horizon_display_y), (mountain_location-mountain_width, horizon_display_y), (mountain_location+mountain_asymmetry, horizon_display_y - mountain_height) )

            mountain_longitude = mountain_longitude + 0.01
            mountain_location = ((mountain_longitude*earth.radius - vehicle.longitude *earth.radius) % 100000 - 100000/2) / self.scale + vehicle.r_display[0] 
            mountain_height = 2000/self.scale
            mountain_width = 10000/self.scale
            mountain_asymmetry = -2000/self.scale
            mountain_4 = ( (mountain_location + mountain_width, horizon_display_y), (mountain_location-mountain_width, horizon_display_y), (mountain_location+mountain_asymmetry, horizon_display_y - mountain_height) )

            pygame.draw.polygon(screen,[0,255,min(255,max(0,int(alt*self.scale/200))),50],mountain_1,0)
            pygame.draw.polygon(screen,[0,255,min(255,max(0,int(alt*self.scale/200))),50],mountain_2,0)
            pygame.draw.polygon(screen,[0,255,min(255,max(0,int(alt*self.scale/200))),50],mountain_3,0)
            pygame.draw.polygon(screen,[0,255,min(255,max(0,int(alt*self.scale/200))),50],mountain_4,0)
            #pygame.draw.polygon(screen,[0,255,min(255,max(0,int(alt*self.scale/200))),50],mountain_5,0)
            #pygame.draw.polygon(screen,[0,255,min(255,max(0,int(alt*self.scale/200))),50],mountain_6,0)
            #pygame.draw.polygon(screen,[0,255,min(255,max(0,int(alt*self.scale/200))),50],mountain_7,0)
            #pygame.draw.polygon(screen,[0,255,min(255,max(0,int(alt*self.scale/200))),50],mountain_8,0)
            #pygame.draw.polygon(screen,[0,255,min(255,max(0,int(alt*self.scale/200))),50],mountain_9,0)
            #pygame.draw.polygon(screen,[0,255,min(255,max(0,int(alt*self.scale/200))),50],mountain_10,0)

            ocean = ( (10000, alt+vehicle.r_display[1]), (-10000, alt+vehicle.r_display[1]), (-10000, 10000), (10000, 10000) )
            pygame.draw.polygon(screen,game_constants.dark_blue,ocean,0)

            
            #mountain_height = 10000/self.scale
            #mountain_location = (-vehicle.horizontal_position + 0) / self.scale
            #mountain_width = 10000/self.scale
            #mountain_asymmetry = 0/self.scale



    def draw_text(self,screen,sim,game,vehicle,earth,game_constants):

        # Giant set of stuff used for displaying
        day = sim.time/86400.0
        ddd = day - day%1
        hour = ((day - ddd ) * 24)
        hh = hour - hour%1
        minute = (hour - hh ) * 60
        mm = minute - minute % 1
        second = (minute - mm) * 60
        ss = second - second % 1
        output_string = "day:hr:min:sec: %03d:%02d:%02d:%02d" % (ddd,hh,mm,ss)

        # do not run faster than max frame rate
        game.my_clock.tick(game.frame_rate)    
        game.delta_real_time = game.my_clock.get_time()

        # Blit to the screen
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,50])

        # display the time zoom
        time_zoom = sim.dt * game.dt_zoom_ratio / game.frame_rate
        output_string = "time zoom ratio (real:game): %03d:1" % (time_zoom)
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,70])
        output_string = "dt %f" % (sim.dt*game.dt_zoom_ratio)
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,110])
        output_string = "dt_real_time %f" % game.delta_real_time
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,130])
        output_string = "for_loop %d" % game.dt_zoom_ratio 
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,150])

        # print out acceleration
        current_g = vehicle.a_mag/earth.g0
        output_string = "accel %f Earth g's" % current_g
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,170])

        # print out velocity
        output_string = "velocity %d m/s" % numpy.linalg.norm(vehicle.v)
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,190])

        # print out altitude
        alt_km = numpy.linalg.norm(vehicle.r)/1000.0 - earth.radius/1000.0
        output_string = "altitude %10.1f km" % alt_km
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,210])

        # print out perigee
        perigee_km = vehicle.rp/1000.0 - 6378.0
        output_string = "perigee %d km" % perigee_km
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,230])

        # print out apogee
        apogee_km = vehicle.ra/1000.0 - 6378.0
        output_string = "apogee %d km" % apogee_km
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,250])

        # argument of perigee
        longitude_deg = vehicle.longitude * 180.0/math.pi
        output_string = "longitude %f deg" % longitude_deg 
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,270])

        # propellant mass
        output_string = "propellant mass %d kg" % vehicle.dv_propellant_mass
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,290])

        # ideal dv
        output_string = "dv ideal %d m/s" % vehicle.dv_ideal
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,310])

        # zoom in
        output_string = self.zoom_list[self.zoom_index]
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,330])

        # screen center options
        output_string_1 = "%d: " % self.center_x
        output_string_2 = "%d: " % self.center_y
        output_string_3 = "%d: " % self.scale
        output_string_4 = "%s: " % self.pan_list[self.pan_index]
        text = game.font.render(output_string_1 + output_string_2 + output_string_3 + output_string_4,True,game_constants.white)
        screen.blit(text, [300,350])

        # zoom in
        output_string = self.viewing_angle_list[self.viewing_angle_index]
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,370])

        # zoom in
        output_string = "%s: " % game.mode_list[game.mode_index]
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,390])

        # legend
        display_line = 410
        output_string = "space bar to thrust"
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,display_line])
        display_line = display_line + 20

        output_string = "right arrow to rotate to the right"
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,display_line])
        display_line = display_line + 20

        output_string = "left arrow to rotate to the left"
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,display_line])
        display_line = display_line + 20

        output_string = "up arrow to increase game speed"
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,display_line])
        display_line = display_line + 20

        output_string = "down arrow to decrease game speed"
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,display_line])
        display_line = display_line + 20

        output_string = "p-key to loop through pan-type list"
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,display_line])
        display_line = display_line + 20

        output_string = "v-key to loop through pan-type list"
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,display_line])
        display_line = display_line + 20

        output_string = "mouse click and hold to pan"
        text = game.font.render(output_string,True,game_constants.white)
        screen.blit(text, [300,display_line])
        display_line = display_line + 20
