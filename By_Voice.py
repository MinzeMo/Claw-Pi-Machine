###############################################################################
# By_Voice.py
#
# Authors: Wenjie Cao (wc585)
#          Ramita Pinsuwannakub (rp625)
#          Minze Mo (mm2943)
#
# Date:    December 8st 2018
#
# Description:
# This scirpt is used for voice mode
# Record the voice, perform speech-to-text, and parse the command
# Move the claw according to the command
###############################################################################

#!/usr/bin/env python3
# NOTE: this example requires PyAudio because it uses the Microphone class
import random
import threading
import time
import RPi.GPIO as GPIO
from datetime import datetime
import sys
import pyaudio
import wave
import requests
import json
import subprocess
import pygame
from pygame.locals import *
import os

def move(state_LR, state_FB, d, t):
	
	# Forward and Backward
	# motor 1
	start = time.time()
	while (time.time() - start < t):
		if state_FB == 0:
			if GPIO.input(21):
				state_FB = 1
		if state_FB == 1:
			if d == 'forward' and not GPIO.input(21):
				state_FB = 0
			if d == 'backward' and not GPIO.input(21):
				state_FB = 2
		if state_FB == 2:
			if GPIO.input(21):
				state_FB = 1
				
		if d == 'forward' and state_FB != 0: # forward
			GPIO.output(19, 1)
			GPIO.output(26, 0)

		elif d == 'backward' and state_FB != 2: # Backward
			GPIO.output(19, 0)
			GPIO.output(26, 1)

		else:
			GPIO.output(19, 0)
			GPIO.output(26, 0)

		# Left and Right
		#motor 2				
		if state_LR == 0:
			if GPIO.input(20):
				state_LR = 1
		if state_LR == 1:
			if d == 'left' and not GPIO.input(20):
				state_LR = 0
			if d == 'right' and not GPIO.input(20):
				state_LR = 2
		if state_LR == 2:
			if GPIO.input(20):
				state_LR = 1
		if d == 'left' and state_LR != 0:	# Left
			GPIO.output(6, 0)
			GPIO.output(13, 1)

		elif d == 'right' and state_LR != 2:	# Right
			GPIO.output(6, 1)
			GPIO.output(13, 0)

		else:
			GPIO.output(6, 0)
			GPIO.output(13, 0)
				
	GPIO.output(19, 0)
	GPIO.output(26, 0)
	GPIO.output(6, 0)
	GPIO.output(13, 0)		
	return state_LR, state_FB

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

def left_right_stop():
    GPIO.output(6, 0)
    GPIO.output(13, 0)

def forward_backward_stop():
    GPIO.output(19, 0)
    GPIO.output(26, 0)

def down_up_stop():
    GPIO.output(17, 0)
    GPIO.output(27, 0)


def record_audio(RECORD_SECONDS, WAVE_OUTPUT_FILENAME):
    #--------- SETTING PARAMS FOR OUR AUDIO FILE ------------#
    FORMAT = pyaudio.paInt16    # format of wave
    CHANNELS = 1                # no. of audio channels
    RATE = 44100                # frame rate
    CHUNK = 1024                # frames per audio sample
    #--------------------------------------------------------#

    # creating PyAudio object
    audio = pyaudio.PyAudio()

    # open a new stream for microphone
    # It creates a PortAudio Stream Wrapper class object
    stream = audio.open(format=FORMAT,channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    #----------------- start of recording -------------------#
    print("Listening...")

    # list to save all audio frames
    frames = []

    for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
        # read audio stream from microphone
        data = stream.read(CHUNK,exception_on_overflow=False)
        # append audio data to frames list
        frames.append(data)

    #------------------ end of recording --------------------#
    print("Finished recording.")

    stream.stop_stream()    # stop the stream object
    stream.close()          # close the stream object
    audio.terminate()       # terminate PortAudio

    #------------------ saving audio ------------------------#

    # create wave file object
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')

    # settings for wave file object
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))

    # closing the wave file object
    waveFile.close()

def read_audio(WAVE_FILENAME):
    # function to read audio(wav) file
    with open(WAVE_FILENAME, 'rb') as f:
        audio = f.read()
    return audio

def find_duration(str):
	if str.find('1')!=-1:
		return 1
	elif str.find('2')!=-1:
		return 2
	elif str.find('3')!=-1:
		return 3
	elif str.find('4')!=-1:
		return 4
	elif str.find('5')!=-1:
		return 5
	elif str.find('6')!=-1:
		return 6
	elif str.find('7')!=-1:
		return 7
	else:
		return -1
	
def run():
	
#	os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
#	os.putenv('SDL_FBDEV', '/dev/fb1')
	
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

	# initialize font
	# draw 2 buttons: start and quit
	my_font = pygame.font.Font(None, 50)
	my_buttons = {'restart':(80,200), 'quit':(240, 200), 'record': (160, 100)}

	for my_text, text_pos in my_buttons.items():
		text_surface = my_font.render(my_text, True, WHITE)
		rect = text_surface.get_rect(center=text_pos)
		screen.blit(text_surface, rect)

	# Size and position of each button
	quit_size = my_font.size('quit')
	quit_center = my_buttons['quit']
	restart_size = my_font.size('restart')
	restart_center = my_buttons['restart']
	record_size = my_font.size('record')
	record_center = my_buttons['record']

	pygame.display.flip()
	
	state_LR, state_FB = 0, 2
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
						print 'Quit By Voice Mode...'
						go_back(state_LR, state_FB)
						isQuit = True
						
				if (restart_center[1] - restart_size[1]/2.) <= y <= (restart_center[1] + restart_size[1]/2.):
					if (restart_center[0] - restart_size[0]/2.) <= x <= (restart_center[0] + restart_size[0]/2.):
						print 'Restart By Voice Mode...'
						go_back(state_LR, state_FB)
						state_LR, state_FB = 0, 2
						
				if (record_center[1] - record_size[1]/2.) <= y <= (record_center[1] + record_size[1]/2.):
					if (record_center[0] - record_size[0]/2.) <= x <= (record_center[0] + record_size[0]/2.):
						print 'Record By Voice Mode...'
						state_LR, state_FB = voice_control(state_LR, state_FB)
						screen.fill(BLACK)
						for my_text, text_pos in my_buttons.items():
							text_surface = my_font.render(my_text, True, WHITE)
							rect = text_surface.get_rect(center=text_pos)
							screen.blit(text_surface, rect)
							pygame.display.flip()

		if isQuit:
			break
			
	GPIO.cleanup()
	
def voice_control(state_LR, state_FB):
	
	WHITE = 255, 255, 255	
	BLACK = 0,0,0
	screen_size = [320, 240]
	screen = pygame.display.set_mode(screen_size)	
	screen.fill(BLACK)
	
	my_font = pygame.font.Font(None, 50)
	my_buttons = {'Recording...':(160,80)}

	# Draw button and coordinate
	for my_text, text_pos in my_buttons.items():
		text_surface = my_font.render(my_text, True, WHITE)
		rect = text_surface.get_rect(center=text_pos)
		screen.blit(text_surface, rect)

	pygame.display.flip()	
	
	
	API_ENDPOINT = 'https://api.wit.ai/speech'
	ACCESS_TOKEN = 'HJM6RWOTOSNDFQ4HQXAY26STRROKGT7Q'
	
	cmd='arecord -D plughw:1,0 -d 3 --rate 44100 --format S16_LE -c1 out_123_machine.wav'
	subprocess.check_output(cmd, shell=True)   
	# get a sample of the audio that we recorded before. 
	audio = read_audio('out_123_machine.wav')#Yamaha-V50-Synbass-1-C2

	# defining headers for HTTP request
	headers = {'authorization': 'Bearer ' + ACCESS_TOKEN,
				'Content-Type': 'audio/wav'}

	#Send the request as post request and the audio as data
	resp = requests.post(API_ENDPOINT, headers = headers,data = audio)

	#Get the text
	data = json.loads(resp.content)
	
	str="hello"
	str =data['_text']
	print str
	
	my_font = pygame.font.Font(None, 25)
	my_buttons = {str:(160, 200)}

	# Draw button and coordinate
	for my_text, text_pos in my_buttons.items():
		text_surface = my_font.render(my_text, True, WHITE)
		rect = text_surface.get_rect(center=text_pos)
		screen.blit(text_surface, rect)

	pygame.display.flip()
	
	duration=2
	if find_duration(str)!=-1:
		duration=find_duration(str)
	
	start=0
	
	if str.find('left')!=-1:#left
		state_LR, state_FB = move(state_LR, state_FB, 'left', duration)
		print 'go left for %d seconds' % (duration)

			
	elif str.find('right')!=-1 or str.find('ride')!=-1:#right
		state_LR, state_FB = move(state_LR, state_FB, 'right', duration)
		if str.find('ride')!=-1:
			str=str.replace('ride','right')
		print 'go right for %d seconds' % (duration)
		
	elif str.find('head')!=-1 or str.find('forward')!=-1:#forward
		state_LR, state_FB = move(state_LR, state_FB, 'forward', duration)
		print 'go ahead for %d seconds' % (duration)
		
	elif str.find('back')!=-1:#backward
		state_LR, state_FB = move(state_LR, state_FB, 'backward', duration)
		print 'go back for %d seconds' % (duration)
		
	elif str.find('down')!=-1:#down
		GPIO.output(17, 1)
		GPIO.output(27, 0)
		time.sleep(duration)
		GPIO.output(17, 0)
		GPIO.output(27, 0)
		print 'go down for %d seconds' % (duration)

	elif str.find('up')!=-1:#up
		GPIO.output(17, 0)
		GPIO.output(27, 1)
		time.sleep(duration)
		GPIO.output(17, 0)
		GPIO.output(27, 0)
		print 'go up for %d seconds' % (duration)

	return state_LR, state_FB
			
