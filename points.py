import sys
import requests
import json
from time import sleep

file_string = 'points_table.json'


def load_file() -> [dict]:
	with open(file_string) as file:
		return json.load(file)


# checks if a user currently exists in points_table
# returns true if they are and false if not
def user_exists_check(user: [str]) -> [bool]:
	points_dict = load_file()
	return user in points_dict


def add_user(user: [str]):
	points_dict = load_file()
	points_dict[user] = 0
	with open (file_string, 'w') as file:
		json.dump(points_dict, file, indent=4, sort_keys=True)


def get_viewers() -> [str]:
	url = r'https://tmi.twitch.tv/group/user/gay_zach/chatters'
	names = requests.get(url).json()

	# avoid getting timed out
	sleep(0.5)

	# formatted string
	return names['chatters']['viewers'] + names['chatters']['moderators']


def get_points(user: [str]) -> [int]:
	points_dict = load_file()
	return points_dict[user]


def get_bot() -> [tuple]:
	points_dict = load_file()
	return sorted(points_dict.items(), key=lambda kv: kv[1])


def update_points(usernames: [str]):
	# reads points_table.json as points_dict
	# edit points_dict for everyone's points
	# re-write points_table.json with edited points_dict
	points_dict = load_file()

		# check if there is a new user in chat, then give everyone points
	for user in usernames:
		if user not in['notstraightbot', 'skinnyseahorse']:
			if user not in points_dict:
				points_dict[user] = 100
			elif user in ['gay_zach', 'hwangbroxd']:
				points_dict[user] += 3
			else:
				points_dict[user] += 1
	with open (file_string, 'w') as file:
		json.dump(points_dict, file, indent=4, sort_keys=True)


def add_points(user: [str], points: [int]):
	points_dict = load_file()
	if user in ['everyone', 'all', 'everybody']:
		usernames = get_viewers()
		for x in usernames:
			if x not in ['skinnyseahorse', 'notstraightbot']:
				points_dict[x] += points
	else:
		points_dict[user] += points
	with open (file_string, 'w') as file:
		json.dump(points_dict, file, indent=4, sort_keys=True)


def mult_points(user: [str], multiplier: [int]):
	points_dict = load_file()
	if user in ['everyone', 'all', 'everybody']:
		usernames = get_viewers()
		for x in usernames:
			if x not in ['skinnyseahorse', 'notstraightbot']:
				points_dict[x] *= multiplier
	else:
		points_dict[user] *= multiplier
	with open (file_string, 'w') as file:
		json.dump(points_dict, file, indent=4, sort_keys=True)


def div_points(user: [str], multiplier: [int]):
	points_dict = load_file()
	if user in ['everyone', 'all', 'everybody']:
		usernames = get_viewers()
		for x in usernames:
			if x not in ['skinnyseahorse', 'notstraightbot']:
				points_dict[x] //= multiplier
	else:	
		points_dict[user] //= multiplier

	with open (file_string, 'w') as file:
		json.dump(points_dict, file, indent=4, sort_keys=True)


def set_points(user: [str], points: [int]):
	points_dict = load_file()
	if user in ['everyone', 'all', 'everybody']:
		usernames = get_viewers()
		for x in usernames:
			if x not in ['skinnyseahorse', 'notstraightbot']:
				points_dict[x] = points
	else:
		points_dict[user] = points
	with open (file_string, 'w') as file:
		json.dump(points_dict, file, indent=4, sort_keys=True)


def donate_points(donator: [str], recipient: [str], value: [int]):
	points_dict = load_file()
	points_dict[donator] -= value
	points_dict[recipient] += value
	with open (file_string, 'w') as file:
		json.dump(points_dict, file, indent=4, sort_keys=True)
