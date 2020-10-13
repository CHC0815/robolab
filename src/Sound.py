"""Sounds Module"""
from ev3dev.ev3 import Sound

def play_startup():
    return Sound.play('start.wav')

def play_obstacle():
    return Sound.play('obstacle.wav')

