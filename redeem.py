import wave
from pygame import mixer
from pynput import keyboard
from time import sleep

lines = 97 # numpad 1
skele = 98 # numpad 2
off = 96 # numpad 0


def play_sound(cmd: str):
	# if a sound is already playing, reset the mixer in case there's a different sample rate
	if mixer.get_init() != None:
		mixer.quit()

	# initialize keyboard controller
	controller = keyboard.Controller()

	# turn off any obs screen effects in case it wasn't stopped before
	effects_off(controller)

	# file_name refers to the .wav audio files to be played
	file_name = f'resources/{cmd}.wav'

	# initialize the mixer with the correct sample rate
	with wave.open(file_name, mode='rb') as music:
		mixer.init(wave.Wave_read.getframerate(music))
		wave.Wave_read.close(music)

	# turn off effects if applicable
	if cmd in ['dejavu', 'gas', '90s']:
		effect_on(controller, lines)
	elif cmd == 'skeleton':
		effect_on(controller, skele)

	# load and play music
	mixer.music.load(file_name)
	mixer.music.set_volume(0.08)
	mixer.music.play()

	# wait until the music is finished
	# if music is stopped abruptly (by another user redeeming), get_busy() will throw an error
	try:
		while mixer.music.get_busy():
			sleep(0.1)
	except:
		return

	effects_off(controller)
	mixer.quit()


def effect_on(controller, key: int):
	controller.press(keyboard.KeyCode(key))
	sleep(0.1) # need this for obs to read macro
	controller.release(keyboard.KeyCode(key))

def effects_off(controller):
	controller.press(keyboard.KeyCode(off)) # F5
	sleep(0.1) # need this for obs to read macro
	controller.release(keyboard.KeyCode(off))