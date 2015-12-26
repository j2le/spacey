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
from rk4 import rk4_three_body
from initialize_vehicle import initialize_vehicle
from initialize_moon import initialize_moon
import game_constants
from vehicle import vehicle
from game import game
from display import display
from sim import sim
from moon import moon
from earth import earth
from flight_computer import flight_computer
import gradients
from gradients import genericFxyGradient
import random

# top priority
#  *get on orbit looking solid
#  *parallax
#  *infinite zoom for vector drawings
#  *icons
#  *start on a board
#  *sidebar options
#  *provide zoom based icons
#  *define atmosphere parameters for each planet object thing
#  *differentiate between inertial and earth relative velocity 
#  *make moon horzon work like earth horizon view for propulsive landing 
#  *optionally scale the rocket with zoom
#  *j2 effects for asteroids
#  *rendezvous problem
#  *add a zoom that includes landing point
#  *make zooms slick rather than cheap
#  * make boards

# fix time zoom to have more options
#  * Pause
# add boards
# Zoom and mult-screen
#   * Click zoom to
#   * split screen into 2 screens 
# make display not jittery
# add lift and drag vector
# reentry attitude dynamics
# move reentry flap
# stage separation model
# cubic earth gravity field
# make interpolation smooth
# compute the angle of attack
# make vehicle move relative to altitude in horizon view
# change parent body for reference
# switch when reaching sphere of influence of new body
# add propellant for attitude control
# add 3-view 
# add sun and interplanetary
# make read out better
# draw a line to aries and aquarius
# Draw Earth land shadows
# slow the rate of change of the orbit
# Draw vector to the sun
# Draw vector to the moon
# add arrows to various planets and features
# add a ground station
# add the sun
# add display for time sun
# switch to trim thrusters
# @todo display sim time versus real time
# make a board, one that teaches something
#  * reach a target orbit
#  * stay in communication with a sat
# Amazing space pictures
#  * Earth and Moon from magellan
#  * Saturn from Gailleo leaving
# add heating indicators
# add flight path angles
# add separation feature
# allow controlling of multiple stages
# add parachutes
# propagation of 3rd body needs to be added to predictor


# Fancify the following
# altitude marker
# make navigation optional

# =======================================
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

# initialize moon
earth = earth()

# initialize moon
moon = moon()

# initialize vehicle state
vehicle = vehicle(scenario,moon)

# initialize display
display = display(scenario,game)

# initialize truth
sim = sim()

# initialize flight computer
flight_computer = flight_computer()

# begin the loop fro the game
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
      if (numpy.linalg.norm(vehicle.r - moon.r) < moon.r_soi):
         parent_body = moon
         sibling_body = earth
         # transfer smoothly
         if vehicle.parent_body == "earth":
            vehicle.r_parent = vehicle.r_parent - moon.r
            vehicle.v_parent = vehicle.v_parent - moon.v
         vehicle.parent_body = "moon"
      else:
         parent_body = earth
         sibling_body = moon
         if vehicle.parent_body == "moon": 
            vehicle.r_parent = vehicle.r_parent + moon.r
            vehicle.v_parent = vehicle.v_parent + moon.v
         vehicle.parent_body = "earth"
          

      # vehicle should always track the body relative to the parent body
      vehicle.update(sim, parent_body.mu, sibling_body.mu, sibling_body.r, parent_body.radius, sim.time, parent_body.omega)

      # update position and velocity in the inertial frame
      vehicle.r = parent_body.r + vehicle.r_parent
      vehicle.v = parent_body.v + vehicle.v_parent

      # update moons
      moon.update(sim,earth.mu)

      # update planets
      earth.update(sim)

    # Do guidance
    # Heads up display
    #r_list = guidance(vehicle.r,vehicle.v,vehicle.period,display.scale,display.center_x,display.center_y)
    flight_computer.update(vehicle,display,parent_body,sibling_body)

    # update the display information
    display.update(sim,screen,game,game_constants,earth,moon,vehicle)

    # Flip the display, wait out the clock tick
    pygame.display.flip()

# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit ()


