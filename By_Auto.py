###############################################################################
# By_Auto.py
#
# Authors: Wenjie Cao (wc585)
#          Ramita Pinsuwannakub (rp625)
#          Minze Mo (mm2943)
#
# Date:    December 8st 2018
#
# Description:
# This scirpt is used for auto mode
# The claw perform object detection and capture the doll
###############################################################################

import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import pygame
from pygame.locals import *
import os

CLAW_P = (220 ,320)
e = 30

def go_back(state_LR, state_FB):
	left_stop, backward_stop = False, False
	while True:
		if state_FB == 0:		
			GPIO.output(19, 0)
			GPIO.output(26, 1)
			time.sleep(1)
			state_FB = 1
		elif state_FB == 1:
			GPIO.output(19, 0)
			GPIO.output(26, 1)
			if not GPIO.input(21):
				state_FB = 2
		elif state_FB == 2:
			GPIO.output(19, 0)
			GPIO.output(26, 0)
			backward_stop = True
		else:
			print 'State_FB Invalid'
		
		if state_LR == 2:		
			GPIO.output(6, 0)
			GPIO.output(13, 1)
			time.sleep(1)
			state_LR = 1
		elif state_LR == 1:
			GPIO.output(6, 0)
			GPIO.output(13, 1)
			if not GPIO.input(20):
				state_LR = 0
		elif state_LR == 0:
			GPIO.output(6, 0)
			GPIO.output(13, 0)
			left_stop = True
		else:
			print 'State_LR Invalid'
		if backward_stop and left_stop:
			break

def move(x, y, state_LR, state_FB):
	print 'moving'
	isX, isY = False, False

	
	if x < CLAW_P[0]-e:
		# left
		dlr = 'left'

	elif x > CLAW_P[0]+e:
		# right
		dlr = 'right'
	else:
		dlr = 'stop'
		isX = True
	
	if y < CLAW_P[1]-e:
		# backward
		dfb = 'backward'		
					
	elif y > CLAW_P[1]+e:
		# forward
		dfb = 'forward'
	else:
		dfb = 'stop'
		isY = True
	
	state_LR, state_FB = state_transition(state_LR, state_FB, dlr, dfb)
	
	return isX, isY, state_LR, state_FB
	
def state_transition(state_LR, state_FB, dlr, dfb):
	
	# Forward and Backward
	# motor 1
	if state_FB == 0:
		if GPIO.input(21):
			state_FB = 1
	if state_FB == 1:
		if dfb == 'forward' and not GPIO.input(21):
			state_FB = 0
		if dfb == 'backward' and not GPIO.input(21):
			state_FB = 2
	if state_FB == 2:
		if GPIO.input(21):
			state_FB = 1
			
	if dfb == 'forward' and state_FB != 0: # forward
		GPIO.output(19, 1)
		GPIO.output(26, 0)
		print 'forward'
	elif 'backward' and state_FB != 2: # Backward
		GPIO.output(19, 0)
		GPIO.output(26, 1)
		print 'backward'

	else:
		GPIO.output(19, 0)
		GPIO.output(26, 0)

	# Left and Right
	#motor 2				
	if state_LR == 0:
		if GPIO.input(20):
			state_LR = 1
	if state_LR == 1:
		if dlr == 'left' and not GPIO.input(20):
			state_LR = 0
		if dlr == 'right' and not GPIO.input(20):
			state_LR = 2
	if state_LR == 2:
		if GPIO.input(20):
			state_LR = 1
	if dlr == 'left' and state_LR != 0:	# Left
		GPIO.output(6, 0)
		GPIO.output(13, 1)
		print 'Left'
	elif dlr == 'right' and state_LR != 2:	# Right
		GPIO.output(6, 1)
		GPIO.output(13, 0)
		print 'Right'
	else:
		GPIO.output(6, 0)
		GPIO.output(13, 0)
	return state_LR, state_FB
	
def drop(state_LR, state_FB):
	left_stop, backward_stop = False, False
	while True:

		if state_FB == 0:		
			GPIO.output(19, 0)
			GPIO.output(26, 1)
			time.sleep(1)
			state_FB = 1
		elif state_FB == 1:
			GPIO.output(19, 0)
			GPIO.output(26, 1)
			if not GPIO.input(21):
				state_FB = 2
		elif state_FB == 2:
			GPIO.output(19, 0)
			GPIO.output(26, 0)
			backward_stop = True
		else:
			print 'State_FB Invalid'
		
		if state_LR == 2:		
			GPIO.output(6, 0)
			GPIO.output(13, 1)
			time.sleep(1)
			state_LR = 1
		elif state_LR == 1:
			GPIO.output(6, 0)
			GPIO.output(13, 1)
			if not GPIO.input(20):
				state_LR = 0
		elif state_LR == 0:
			GPIO.output(6, 0)
			GPIO.output(13, 0)
			left_stop = True
		else:
			print 'State_LR Invalid'
		if backward_stop and left_stop:
			break
	GPIO.output(17, 1)	
	GPIO.output(27, 0)
	time.sleep(1.5)
	GPIO.output(17, 0)	
	GPIO.output(27, 1)
	time.sleep(2)
	GPIO.output(17, 0)	
	GPIO.output(27, 0)
			
def capture(color, state_LR, state_FB):
	
	cap = cv2.VideoCapture(0)
	if color == 'green':
		lower = np.array([29,86,6])
		upper = np.array([64,255,255])	

	elif color == 'yellow':
		lower = np.array([15,100,110])
		upper = np.array([30,255,255])
		
	elif color == 'blue':
		lower = np.array([90,50,40])
		upper = np.array([130,255,255])


	try:
		while(True):

			# Take each frame
			_, frame = cap.read()

			# Convert BGR to HSV
			hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
			
			mask = cv2.inRange(hsv, lower, upper)
			
			# Bitwise-AND mask and original image
			res = cv2.bitwise_and(frame,frame, mask = mask)

			a, b = np.where(mask == 255)
			
			if len(a) > 5000:
				x, y = np.average(a), np.average(b)
				cv2.circle(res,(int(y), int(x)), 5, (0,0,255), 5)
				isX, isY, state_LR, state_FB = move(x, y, state_LR, state_FB)

				if (isX or state_LR != 1) and (isY or state_FB != 1):
					print 'Capturing....'

					GPIO.output(6, 0)
					GPIO.output(13, 0)
					GPIO.output(19, 0)
					GPIO.output(26, 0)
					break
			else:
				print 'No detection'
				GPIO.output(6, 0)
				GPIO.output(13, 0)
				GPIO.output(19, 0)
				GPIO.output(26, 0)
				break



#			cv2.imshow('frame',frame)
#			cv2.imshow('mask',mask)
#			cv2.imshow('res',res)
			
#			k = cv2.waitKey(5) & 0xFF
#			if k == 27:
#				return state_LR, state_FB
#				break
	except KeyboardInterrupt:
		GPIO.cleanup()

	GPIO.output(17, 1)	
	GPIO.output(27, 0)
	time.sleep(3.75)
	GPIO.output(17, 0)	
	GPIO.output(27, 1)
	time.sleep(3.75)
	GPIO.output(17, 0)	
	GPIO.output(27, 0)	
	
	cv2.destroyAllWindows()
	return state_LR, state_FB

def first_move():
	GPIO.output(19, 1)
	GPIO.output(26, 0)
	time.sleep(3.5)
	GPIO.output(19, 0)
	GPIO.output(26, 0)
	
def search(color):
	state_LR = 0
	cap = cv2.VideoCapture(0)
	if color == 'green':
		lower = np.array([29,86,6])
		upper = np.array([64,255,255])

	elif color == 'yellow':
		lower = np.array([15,100,110])
		upper = np.array([30,255,255])

	elif color == 'blue':
		lower = np.array([90,50,40])
		upper = np.array([130,255,255])

	GPIO.output(6, 1)
	GPIO.output(13, 0)
	
	try:
		while(True):
			if state_LR == 0 and GPIO.input(20):
				state_LR = 1
			if state_LR == 1 and not GPIO.input(20):
				state_LR = 2
			
			_, frame = cap.read()
			# Convert BGR to HSV
			hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
			
			mask = cv2.inRange(hsv, lower, upper)
			
			# Bitwise-AND mask and original image
			res = cv2.bitwise_and(frame,frame, mask = mask)

			a, b = np.where(mask == 255)
			if len(a) > 5000:
				time.sleep(0.2)
				GPIO.output(6, 0)
				GPIO.output(13, 0)
				return True, state_LR
			if state_LR == 2:
				GPIO.output(6, 0)
				GPIO.output(13, 0)
				return False, state_LR
#			cv2.imshow('frame',frame)
#			cv2.imshow('mask',mask)
#			cv2.imshow('res',res)

#			k = cv2.waitKey(5) & 0xFF
#			if k == 27:
#				break

	except KeyboardInterrupt:
		GPIO.cleanup()

def run():
	
	GPIO.setmode(GPIO.BCM)

	#to L293D to FW-BW (motor1) 
	GPIO.setup(19, GPIO.OUT)
	GPIO.setup(26, GPIO.OUT)

	#to L293D to L-R (motor2) 
	GPIO.setup(6, GPIO.OUT)
	GPIO.setup(13, GPIO.OUT)

	#to L293D to U-D (motor3)  
	GPIO.setup(17, GPIO.OUT)
	GPIO.setup(27, GPIO.OUT)

	#limit switch
	GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # motor 2 L-R
	GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # motor 1 FW-BW
	
	WHITE = 255, 255, 255
	BLACK = 0,0,0
	screen_size = [320, 240]
	screen = pygame.display.set_mode(screen_size)
	screen.fill(BLACK)

	my_font = pygame.font.Font(None, 30)
	my_buttons = {'restart':(80,220), 'quit':(240, 220), 'Keroppi': (160, 100), 'Winnie the Pooh': (160, 140), 'Doraemon': (160, 180), 'Choose Your Doll': (160, 40)}

	for my_text, text_pos in my_buttons.items():
		text_surface = my_font.render(my_text, True, WHITE)
		rect = text_surface.get_rect(center=text_pos)
		screen.blit(text_surface, rect)

	# Size and position of each button
	quit_size = my_font.size('quit')
	quit_center = my_buttons['quit']
	restart_size = my_font.size('restart')
	restart_center = my_buttons['restart']
	keroppi_size = my_font.size('Keroppi')
	keroppi_center = my_buttons['Keroppi']
	winnie_size = my_font.size('Winnie the Pooh')
	winnie_center = my_buttons['Winnie the Pooh']
	doraemon_size = my_font.size('Doraemon')
	doraemon_center = my_buttons['Doraemon']

	pygame.display.flip()

	isQuit = False
	while(True):
			
		for event in pygame.event.get():
			
			# Check if there is a mouse-click event
			if (event.type is MOUSEBUTTONDOWN):
				pos = pygame.mouse.get_pos()
			elif (event.type is MOUSEBUTTONUP):
				pos = pygame.mouse.get_pos()
				x, y = pos
							
				# Check if quit button clicked
				# If yes, exit the program
				if (quit_center[1] - quit_size[1]/2.) <= y <= (quit_center[1] + quit_size[1]/2.):
					if (quit_center[0] - quit_size[0]/2.) <= x <= (quit_center[0] + quit_size[0]/2.):
						print 'Quit By Hand Mode...'
						go_back(state_LR, state_FB)
						isQuit = True
						
				if (restart_center[1] - restart_size[1]/2.) <= y <= (restart_center[1] + restart_size[1]/2.):
					if (restart_center[0] - restart_size[0]/2.) <= x <= (restart_center[0] + restart_size[0]/2.):
						print 'Restart By Hand Mode...'
						go_back(state_LR, state_FB)
						state_LR, state_FB = 0, 2
						
				if (keroppi_center[1] - keroppi_size[1]/2.) <= y <= (keroppi_center[1] + keroppi_size[1]/2.):
					if (keroppi_center[0] - keroppi_size[0]/2.) <= x <= (keroppi_center[0] + keroppi_size[0]/2.):
						print 'Start capture Keroppi'
						first_move()
						isfound, state_LR = search('green')
						if isfound:
							state_LR, state_FB = capture('green', state_LR, 1)
							drop(state_LR, state_FB)
						else:
							print 'The object cannot be found'
							go_back(state_LR, 1)
							
				if (winnie_center[1] - winnie_size[1]/2.) <= y <= (winnie_center[1] + winnie_size[1]/2.):
					if (winnie_center[0] - winnie_size[0]/2.) <= x <= (winnie_center[0] + winnie_size[0]/2.):
						print 'Start capture Winnie the Pooh'
						first_move()
						isfound, state_LR = search('yellow')
						if isfound:
							state_LR, state_FB = capture('yellow', state_LR, 1)
							drop(state_LR, state_FB)
						else:						
							print 'The object cannot be found'
							go_back(state_LR, 1)

				if (doraemon_center[1] - doraemon_size[1]/2.) <= y <= (doraemon_center[1] + doraemon_size[1]/2.):
					if (doraemon_center[0] - doraemon_size[0]/2.) <= x <= (doraemon_center[0] + doraemon_size[0]/2.):
						print 'Start capture Doraemon'
						first_move()
						isfound, state_LR = search('blue')
						if isfound:
							state_LR, state_FB = capture('blue', state_LR, 1)
							drop(state_LR, state_FB)
						else:
							print 'The object cannot be found'
							go_back(state_LR, 1)
		if isQuit:
			break
	GPIO.cleanup()
