import json
import os
import requests
from random import randint
from time import sleep

everyone = ['everybody', 'everyone', 'all']
admins = ['gay_zach', 'hwangbroxd']

def load_file(file_name: str) -> dict:
	with open(file_name) as file:
		return json.load(file)

def write_file(file_name: str, rewrite):
	with open(file_name, 'w') as file:
		json.dump(rewrite, file, indent=4)

def remove_file(file_name: str):
	if os.path.exists(file_name):
		os.remove(file_name)

def load_blacklist() -> dict:
	with open('json/blacklist.json') as file:
		return json.load(file)

def write_blacklist(rewrite: dict):
	with open('json/blacklist.json') as file:
		json.dump(rewrite, file, indent=4)

def file_exists(file_name: str) -> bool:
	return os.path.exists(file_name)

def get_viewers() -> [str]:
	url = r'https://tmi.twitch.tv/group/user/gay_zach/chatters'
	names = requests.get(url).json()

	# avoid getting timed out
	sleep(0.1)

	# formatted string
	return names['chatters']['viewers'] + names['chatters']['moderators']
	
def rng(min_value: int, max_value: int) -> int:
	return randint(min_value, max_value)