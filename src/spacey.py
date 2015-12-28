# Import a library of functions called 'pygame'
import pygame
import pygame.gfxdraw
import math
import numpy
import sys
sys.path.append("math")
sys.path.append("truth")
sys.path.append("game")
sys.path.append("config")
sys.path.append("flight_computer")
sys.path.append("3rdparty/gradients")
from rv2oe import rv2oe
from rk4 import rk4
from initialize_vehicle import initialize_vehicle
import game_constants
from vehicle import vehicle
from game import game
from display import display
from sim import sim
from earth import earth
from flight_computer import flight_computer
import random

# =======================================

# Initialize the game engine
pygame.init()

# scenario
scenario = "leo"
#scenario = "moon"
#scenario = "entry"

# Set the height and width of the screen
screen=pygame.display.set_mode(game_constants.size)

#Loop until the user clicks the close button.
game = game(pygame)

# initialize earth
earth = earth()

# initialize vehicle state
vehicle = vehicle(scenario)

# initialize display
display = display(scenario,game)

# initialize truth
sim = sim()

# initialize flight computer
flight_computer = flight_computer()

# begin the loop for the game
while game.done==False:

    # http://www.pygame.org/docs/ref/key.html
    # User did something
    for event in pygame.event.get():

        # update the game based on keystrokes
        game.update_events(event,vehicle,display,pygame,sim)

    # for loop around propagation
    for i in range(game.dt_zoom_ratio):

      # update simulation
      sim.update()

      # compute position relative to every body
      # currently inertial frame has origin at the earth
      # check smallest sphere of influence first
      parent_body = earth
      vehicle.parent_body = "earth"
          

      # vehicle should always track the body relative to the parent body
      vehicle.update(sim, parent_body.mu, parent_body.radius, sim.time, parent_body.omega)

      # update position and velocity in the inertial frame
      vehicle.r = parent_body.r + vehicle.r_parent
      vehicle.v = parent_body.v + vehicle.v_parent

      # update planets
      earth.update(sim)

    # Do guidance
    # Heads up display
    #r_list = guidance(vehicle.r,vehicle.v,vehicle.period,display.scale,display.center_x,display.center_y)
    flight_computer.update(vehicle,display,parent_body)

    # update the display information
    display.update(sim,screen,game,game_constants,earth,vehicle)

    # Flip the display, wait out the clock tick
    pygame.display.flip()

# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit ()


