import requests
import operator
from time import sleep

import utilities as util

file_string = 'json/points_table.json'

everyone = ['everybody', 'everyone', 'all']
admins = ['gay_zach', 'hwangbroxd']


def user_exists_check(user: str) -> bool:
	# checks if a user currently exists in points_table
	# returns true if they are and false if not
	points_dict = util.load_file(file_string)
	return user in points_dict


def add_user(user: str):
	points_dict = util.load_file(file_string)
	points_dict[user] = 0
	util.write_file(file_string, points_dict)


def remove_user(user: str):
	points_dict = util.load_file(file_string)
	points_dict.pop(user, None)
	util.write_file(file_string, points_dict)


def get_points(user: str) -> int:
	points_dict = util.load_file(file_string)
	return points_dict[user]


def get_bot() -> list:
	points_dict = util.load_file(file_string)
	return sorted(points_dict.items(), key=lambda kv: kv[1])


def update_points(usernames: [str]):
	# reads points_table.json as points_dict
	# edit points_dict for everyone's points
	# re-write points_table.json with edited points_dict
	points_dict = util.load_file(file_string)

		# check if there is a new user in chat, then give everyone points
	for user in usernames:
		if user not in points_dict:
			points_dict[user] = 100
		elif user in admins:
			points_dict[user] += 3
		else:
			points_dict[user] += 1
	util.write_file(file_string, points_dict)


def change_points(user: str, points: int, op: str):
	# op takes in "+", "-", ...
	ops = {"+": operator.iadd,
           "-": operator.isub,
           "*": operator.imul,
           "/": operator.ifloordiv}
	points_dict = util.load_file(file_string)
	if user in everyone:
		usernames = util.get_viewers()
		blacklist = util.load_file('json/blacklist.json')
		for x in usernames:
			if x not in blacklist:
				points_dict[x] = ops[op](points_dict[x], points)
	else:
		points_dict[user] = ops[op](points_dict[user], points)
	util.write_file(file_string, points_dict)


def set_points(user: str, points: int):
	points_dict = util.load_file(file_string)
	if user in everyone:
		usernames = util.get_viewers()
		blacklist = util.load_file('json/blacklist.json')
		for x in usernames:
			if x not in blacklist:
				points_dict[x] = points
	else:
		points_dict[user] = points
	util.write_file(file_string, points_dict)


def donate_points(donator: str, recipient: str, value: int):
	points_dict = util.load_file(file_string)
	points_dict[donator] -= value
	points_dict[recipient] += value
	util.write_file(file_string, points_dict)
