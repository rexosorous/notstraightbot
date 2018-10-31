import sys
import wave
from pygame import mixer
from pynput import keyboard
from time import sleep


def play_sound(cmd: str):
	if mixer.get_init() != None:
		mixer.quit()
	controller = keyboard.Controller()

	lines_off(controller)

	file_name = f'resources/{cmd}.wav'

	with wave.open(file_name, mode='rb') as music:
		mixer.init(wave.Wave_read.getframerate(music))
		wave.Wave_read.close(music)

	if cmd in ['dejavu', 'gas', '90s']:
		lines_on(controller)

	mixer.music.load(file_name)
	mixer.music.set_volume(0.08)
	mixer.music.play()

	try:
		while mixer.music.get_busy():
			sleep(0.1)
	except:
		return

	if cmd in ['dejavu', 'gas', '90s']:
		lines_off(controller)

	mixer.quit()


def lines_on(controller):
	controller.press(keyboard.KeyCode(112)) # F1
	sleep(0.1) # need this for obs to read macro
	controller.release(keyboard.KeyCode(112))

def lines_off(controller):
	controller.press(keyboard.KeyCode(113)) # F2
	sleep(0.1) # need this for obs to read macro
	controller.release(keyboard.KeyCode(113))