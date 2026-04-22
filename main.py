from config import *
from robot.robot import Robot
from simulation.environment import Environment
from visualization.gui import GUI
import time

robots = [Robot(f"R{i}") for i in range(NUM_ROBOTS)]
env = Environment(robots)

gui = GUI(robots, env)

gui.run()