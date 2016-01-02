import numpy
import display
class game(object):
    def __init__(self,pygame):
        self.done = False
        self.dt_zoom_ratio = 10
        self.dt_zoom_state = "freeze"

        self.frame_rate = 100
        self.mode = "earth_orbit"
        self.mode_list = list()
        self.mode_list.append("earth_orbit")
        self.mode_list.append("earth_entry")
        self.mode_index = 0

        # start clock
        self.my_clock=pygame.time.Clock()

        # fonts
        self.font = pygame.font.Font(None, 25)

        self.init_mode = False

    def update_events(self,event,vehicle,display,pygame,sim):

        # If user clicked close
        if event.type == pygame.QUIT:
            # Flag that we are done so we exit this loop
            self.done=True

        # if you detect a button press
        if (event.type == pygame.KEYDOWN):

           # n flips sign on time step
           if event.key == pygame.K_n:
               sim.dt = -sim.dt

           # m updates mode of game and overwrites current
           if (event.key == pygame.K_m or self.init_mode == True):
               self.init_mode = False
               if self.mode_index >= len(self.mode_list):
                   self.mode_index = self.mode_index - len(self.mode_list)
               if self.mode_list[self.mode_index] == "earth_orbit":
                   display.zoom_index = 0
                   display.pan_index = 0
                   display.pan_angle_index = 0
               elif self.mode_list[self.mode_index] == "earth_entry":
                   display.zoom_index = 5
                   display.pan_index = 1
                   display.viewing_angle_index = 1

           # space bar is for thrusting
           # vehicle update
           if event.key == pygame.K_SPACE:
               vehicle.thrusting = 1

           # rotate the vehicle
           # vehicle update
           if event.key == pygame.K_RIGHT:
               vehicle.delta_attitude = -1.0

           # rotate the vehicle
           # vehicle update
           if event.key == pygame.K_LEFT:
               vehicle.delta_attitude = 1.0

           # increase time step of sim
           # sim update
           if event.key == pygame.K_UP:
               self.dt_zoom_ratio = self.dt_zoom_ratio + 1
               self.dt_zoom_state = "zooming_out"

           # decrease time step of sim
           # sim update
           if event.key == pygame.K_DOWN:
               self.dt_zoom_ratio = self.dt_zoom_ratio - 1
               self.dt_zoom_state = "zooming_in"
               if (self.dt_zoom_ratio < 1):
                  self.dt_zoom_ratio = 1

           # loop through zoom list
           # display update
           #if event.key == pygame.K_z:
           #    display.zoom_index = display.zoom_index + 1;
           #    if display.zoom_index >= len(display.zoom_list):
           #        display.zoom_index = display.zoom_index - len(display.zoom_list)

           # loop through pan list
           # display update
           #if event.key == pygame.K_p:
           #    display.pan_index = display.pan_index + 1;
           #    if display.pan_index >= len(display.pan_list):
           #        display.pan_index = display.pan_index - len(display.pan_list)

           # loop through viewing angle list
           #if event.key == pygame.K_v:
           #    display.viewing_angle_index = display.viewing_angle_index + 1;
           #    if display.viewing_angle_index >= len(display.viewing_angle_list):
           #        display.viewing_angle_index = display.viewing_angle_index - len(display.viewing_angle_list)

           # loop through view type
           if event.key == pygame.K_t:
               display.mode_index = display.mode_index + 1;
               if display.mode_index >= len(display.mode_list):
                   display.mode_index = display.mode_index - len(display.mode_list)

        # detect a button release
        if event.type == pygame.KEYUP:

           # set thrust and acceleration to zero when not thrusting
           # vehicle update
           if event.key == pygame.K_SPACE:
               vehicle.thrusting = 0

           # stop rotating when button is released
           # vehicle update
           if (event.key == pygame.K_LEFT): 
               vehicle.delta_attitude = 0.0

           # stop rotating when button is released
           # vehicle update
           if (event.key == pygame.K_RIGHT):
               vehicle.delta_attitude = 0.0

           # step sim time changes
           if event.key == pygame.K_UP:
               self.dt_zoom_state = "freeze"

           # decrease time step of sim
           # sim update
           if event.key == pygame.K_DOWN:
               self.dt_zoom_state = "freeze"

        # detect a mouse button press
        if event.type == pygame.MOUSEBUTTONDOWN:

            # get the mouse button position
            pos = pygame.mouse.get_pos()

            #print("Row:",row,"Column:",col)
            display.pan_click_1_pos_0 = pos[0]
            display.pan_click_1_pos_1 = pos[1]

            # indicating sim is in pan mode
            display.mouse_down_pan = 1

        # detect a mouse release
        elif event.type == pygame.MOUSEBUTTONUP:

            # move sim out of pan mode 
            display.mouse_down_pan = 0

        # if panning update position let the display zero out       
        if display.mouse_down_pan:
            pos = pygame.mouse.get_pos()
            display.delta_pan_0 = display.delta_pan_0 + pos[0] - display.pan_click_1_pos_0
            display.delta_pan_1 = display.delta_pan_1 + pos[1] - display.pan_click_1_pos_1
            display.pan_click_1_pos_0 = pos[0]
            display.pan_click_1_pos_1 = pos[1]


