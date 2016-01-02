import numpy
import display
class game(object):
    def __init__(self,pygame):
        self.done = False
        self.dt_zoom_ratio = 1
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

           # loop through view type
           if event.key == pygame.K_z:
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
