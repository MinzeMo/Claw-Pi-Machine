###############################################################################
# screen.py
#
# Authors: Wenjie Cao (wc585)
#          Ramita Pinsuwannakub (rp625)
#          Minze Mo (mm2943)
#
# Date:    December 8st 2018
#
# Description:
# This scirpt is the main function of the program
# Create a user interface on piTFT, call the mode specific by the user
###############################################################################

import pygame
from pygame.locals import *
import os
import RPi.GPIO as GPIO
import time
from threading import Timer
import sys
import By_Hand
import By_Voice
import By_Auto


def Level2():
	
#	os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
#	os.putenv('SDL_FBDEV', '/dev/fb1')
	
	WHITE = 255, 255, 255
	BLACK = 0,0,0
	screen_size = [320, 240]
	screen = pygame.display.set_mode(screen_size)
	screen.fill(BLACK)

	# initialize font
	# draw 2 buttons: start and quit
	my_font = pygame.font.Font(None, 50)
	my_buttons = {'Mode selection':(160,50), 'By hand':(160,100), 'By voice': (160,150), 'AUTO': (160,200)}
	quit_font = pygame.font.Font(None,25)
	quit_button = {'quit':(280,220)}

	for my_text, text_pos in my_buttons.items():
		text_surface = my_font.render(my_text, True, WHITE)
		rect = text_surface.get_rect(center=text_pos)
		screen.blit(text_surface, rect)

	for my_text, text_pos in quit_button.items():
		text_surface = quit_font.render(my_text, True, WHITE)
		rect = text_surface.get_rect(center=text_pos)
		screen.blit(text_surface, rect)
		
	pygame.display.flip()

	while True:
		time.sleep(0.2)
			
		for event in pygame.event.get():
			
			# Check if there is a mouse-click event
			if (event.type is MOUSEBUTTONDOWN):
				pos = pygame.mouse.get_pos()
			elif (event.type is MOUSEBUTTONUP):
				pos = pygame.mouse.get_pos()
				x, y = pos
							
				# Size and position of each button
				hand_size = my_font.size('By hand')
				hand_center = my_buttons['By hand']
				voice_size = my_font.size('By voice')
				voice_center = my_buttons['By voice']
				auto_size = my_font.size('AUTO')
				auto_center = my_buttons['AUTO']
				quit_size = quit_font.size('quit')
				quit_center = quit_button['quit']
				
				# Check if quit button clicked
				# If yes, exit the program
				if (quit_center[1] - quit_size[1]/2.) <= y <= (quit_center[1] + quit_size[1]/2.):
					if (quit_center[0] - quit_size[0]/2.) <= x <= (quit_center[0] + quit_size[0]/2.):
						print 'Quit the program...'
						sys.exit(0)
				
				if (hand_center[1] - hand_size[1]/2.) <= y <= (hand_center[1] + hand_size[1]/2.):
					if (hand_center[0] - hand_size[0]/2.) <= x <= (hand_center[0] + hand_size[0]/2.):
						print 'Start By Hand Mode...'
						By_Hand.run()
						
						GPIO.setmode(GPIO.BCM) # BCM mode needs GPIO pin
						
						screen.fill(BLACK)
						for my_text, text_pos in my_buttons.items():
							text_surface = my_font.render(my_text, True, WHITE)
							rect = text_surface.get_rect(center=text_pos)
							screen.blit(text_surface, rect)
						
						for my_text, text_pos in quit_button.items():
							text_surface = quit_font.render(my_text, True, WHITE)
							rect = text_surface.get_rect(center=text_pos)
							screen.blit(text_surface, rect)
							
						pygame.display.flip()
				
				if (auto_center[1] - auto_size[1]/2.) <= y <= (auto_center[1] + auto_size[1]/2.):
					if (auto_center[0] - auto_size[0]/2.) <= x <= (auto_center[0] + auto_size[0]/2.):
						print 'Start Auto Mode...'
						By_Auto.run()
						GPIO.setmode(GPIO.BCM) # BCM mode needs GPIO pin
						
						screen.fill(BLACK)
						for my_text, text_pos in my_buttons.items():
							text_surface = my_font.render(my_text, True, WHITE)
							rect = text_surface.get_rect(center=text_pos)
							screen.blit(text_surface, rect)
						
						for my_text, text_pos in quit_button.items():
							text_surface = quit_font.render(my_text, True, WHITE)
							rect = text_surface.get_rect(center=text_pos)
							screen.blit(text_surface, rect)
							
						pygame.display.flip()

				if (voice_center[1] - voice_size[1]/2.) <= y <= (voice_center[1] + voice_size[1]/2.):
					if (voice_center[0] - voice_size[0]/2.) <= x <= (voice_center[0] + voice_size[0]/2.):
						print 'Start Voice Mode...'
						By_Voice.run()
						GPIO.setmode(GPIO.BCM) # BCM mode needs GPIO pin
						
						screen.fill(BLACK)
						for my_text, text_pos in my_buttons.items():
							text_surface = my_font.render(my_text, True, WHITE)
							rect = text_surface.get_rect(center=text_pos)
							screen.blit(text_surface, rect)
						
						for my_text, text_pos in quit_button.items():
							text_surface = quit_font.render(my_text, True, WHITE)
							rect = text_surface.get_rect(center=text_pos)
							screen.blit(text_surface, rect)
							
						pygame.display.flip()	

def Level1():
	
	#commend these foue lines
	os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
	os.putenv('SDL_FBDEV', '/dev/fb1')
	os.putenv('SDL_MOUSEDRV', 'TSLIB') # Track mouse clicks on piTFT
	os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

	# Configure GPIO25
	GPIO.setmode(GPIO.BCM) # BCM mode needs GPIO pin

	# Initial pygame
	# Set the screen size to 320x240
	pygame.init()

	pygame.mouse.set_visible(False)

	WHITE = 255, 255, 255
	BLACK = 0,0,0
	screen_size = [320, 240]
	screen = pygame.display.set_mode(screen_size)
	screen.fill(BLACK)

	# initialize font
	# draw 2 buttons: start and quit
	my_font = pygame.font.Font(None, 100)
	my_buttons = {'start':(80,200), 'quit':(240,200)}

	for my_text, text_pos in my_buttons.items():
		text_surface = my_font.render(my_text, True, WHITE)
		rect = text_surface.get_rect(center=text_pos)
		screen.blit(text_surface, rect)

	pygame.display.flip()
	
	# the first level
	while True:
		time.sleep(0.2)

		for event in pygame.event.get():
			# Check if there is a mouse-click event
			if (event.type is MOUSEBUTTONDOWN):
				pos = pygame.mouse.get_pos()
			elif (event.type is MOUSEBUTTONUP):
				pos = pygame.mouse.get_pos()
				x, y = pos
							
				# Size and position of each button
				start_size = my_font.size('start')
				start_center = my_buttons['start']
				quit_size = my_font.size('quit')
				quit_center = my_buttons['quit']
				
				# Check if quit button clicked
				# If yes, exit the program
				if (quit_center[1] - quit_size[1]/2.) <= y <= (quit_center[1] + quit_size[1]/2.):
					if (quit_center[0] - quit_size[0]/2.) <= x <= (quit_center[0] + quit_size[0]/2.):
						print 'Quit Button Cliked...'
						sys.exit(0)
				
				# Check if start buttom clicked
				# If yes, go to level 2
				if (start_center[1] - start_size[1]/2.) <= y <= (start_center[1] + start_size[1]/2.):
					if (start_center[0] - start_size[0]/2.) <= x <= (start_center[0] + start_size[0]/2.):
						print 'start Button Cliked...'
						Level2()
						
						screen.fill(BLACK)
						for my_text, text_pos in my_buttons.items():
							text_surface = my_font.render(my_text, True, WHITE)
							rect = text_surface.get_rect(center=text_pos)
							screen.blit(text_surface, rect)
				
						pygame.display.flip()
				else:
					msg = 'Hit at (%d, %d)' %(x, y)
					print msg
				
					# Erase the screen
					screen.fill(BLACK)
				
					# Draw button and coordinate
					text_surface = my_font.render(msg, True, WHITE)
					rect = text_surface.get_rect(center=(screen_size[0]/2, screen_size[1]/2))
					screen.blit(text_surface, rect)
				
					for my_text, text_pos in my_buttons.items():
						text_surface = my_font.render(my_text, True, WHITE)
						rect = text_surface.get_rect(center=text_pos)
						screen.blit(text_surface, rect)
				
					pygame.display.flip()

if __name__=='__main__':
	Level1()
