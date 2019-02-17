###############################################################################
# By_Hand.py
#
# Authors: Wenjie Cao (wc585)
#          Ramita Pinsuwannakub (rp625)
#          Minze Mo (mm2943)
#
# Date:    December 8st 2018
#
# Description:
# This scirpt is used for hand mode
# Move the claw machine according to the input signal
# State machine is used for movement
###############################################################################

import time
import RPi.GPIO as GPIO
import pygame
from pygame.locals import *
import os
import sys

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

def run():

#	os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
#	os.putenv('SDL_FBDEV', '/dev/fb1')
	
	GPIO.setmode(GPIO.BCM)

	#from switch FW-BW (motor1)
	GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	#to L293D to FW-BW (motor1) 
	GPIO.setup(19, GPIO.OUT)
	GPIO.setup(26, GPIO.OUT)

	#from switch L-R (motor2)
	GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	#to L293D to L-R (motor2) 
	GPIO.setup(6, GPIO.OUT)
	GPIO.setup(13, GPIO.OUT)

	#from switch U-D (motor3)
	GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	#to L293D to U-D (motor3)  
	GPIO.setup(17, GPIO.OUT)
	GPIO.setup(27, GPIO.OUT)

	#limit switch
	GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # motor 2 L-R
	GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # motor 1 FW-BW
	
	#state_FB == 1: unpressed the limit swutch
	#state_FB == 0: press FW limit switch
	#state_FB == 2: press BW limit switch
	state_FB = 2
	state_LR = 0

	WHITE = 255, 255, 255
	BLACK = 0,0,0
	screen_size = [320, 240]
	screen = pygame.display.set_mode(screen_size)
	screen.fill(BLACK)

	# initialize font
	# draw 2 buttons: start and quit
	my_font = pygame.font.Font(None, 50)
	my_buttons = {'restart':(80,200), 'quit':(240, 200)}

	for my_text, text_pos in my_buttons.items():
		text_surface = my_font.render(my_text, True, WHITE)
		rect = text_surface.get_rect(center=text_pos)
		screen.blit(text_surface, rect)

	# Size and position of each button
	quit_size = my_font.size('quit')
	quit_center = my_buttons['quit']
	restart_size = my_font.size('restart')
	restart_center = my_buttons['restart']

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
		if isQuit:
			break

		# Forward and Backward
		# motor 1
		if state_FB == 0:
			if GPIO.input(21):
				state_FB = 1
		if state_FB == 1:
			if GPIO.input(5) and not GPIO.input(21):
				state_FB = 0
			if GPIO.input(23) and not GPIO.input(21):
				state_FB = 2
		if state_FB == 2:
			if GPIO.input(21):
				state_FB = 1
		if GPIO.input(5) and state_FB != 0: # forward
			GPIO.output(19, 1)
			GPIO.output(26, 0)
			print 'Forward'
		elif GPIO.input(23) and state_FB != 2: # Backward
			GPIO.output(19, 0)
			GPIO.output(26, 1)
			print 'Backward'

		else:
			GPIO.output(19, 0)
			GPIO.output(26, 0)	
				
		# Left and Right
		#motor 2				
		if state_LR == 0:
			if GPIO.input(20):
				state_LR = 1
		if state_LR == 1:
			if GPIO.input(16) and not GPIO.input(20):
				state_LR = 0
			if GPIO.input(12) and not GPIO.input(20):
				state_LR = 2
		if state_LR == 2:
			if GPIO.input(20):
				state_LR = 1
		if GPIO.input(16) and state_LR != 0:	# Left
			GPIO.output(6, 0)
			GPIO.output(13, 1)
			print 'Left'

		elif GPIO.input(12) and state_LR != 2:	# Right
			GPIO.output(6, 1)
			GPIO.output(13, 0)
			print 'Right'
		else:
			GPIO.output(6, 0)
			GPIO.output(13, 0)	
		
		#motor3
		if (GPIO.input(22)):	# UP
			GPIO.output(17, 0)
			GPIO.output(27, 1)
			print 'up'
		elif (GPIO.input(4)):	# DOWN
			GPIO.output(17, 1)
			GPIO.output(27, 0)
			print 'down'
		else:
			GPIO.output(17, 0)
			GPIO.output(27, 0)
	GPIO.cleanup()

