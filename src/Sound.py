"""Sounds Module"""
from ev3dev.ev3 import Sound

def play_startup():
    return Sound.play('/home/robot/src/music/start.wav')

def play_node():
    return Sound.play('/home/robot/src/music/node.wav')

def play_obstacle():
    return Sound.play('/home/robot/src/music/obstacle.wav')

def play_victory():
    return Sound.play('/home/robot/src/music&victory.wav')
