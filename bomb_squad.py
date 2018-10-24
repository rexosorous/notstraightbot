import sys
import json
import random
import os

import points
import utilities as util

# UNRELATED NOTES bc i won't remember unless it's in here
# users can guarantee a win on lottery by buying max tickets and they'll always make a profit, find some way to balance this
# should it be possible for more than one event (not the same one) to happen at the same time?
# make variable names consistent: events should have 'players' not 'users'
# find a way to split up !bomb commands

# an irc remake of: https://www.youtube.com/watch?v=GXTRNSuC_YQ
#
# 1. inform users that bomb squad event will start soon
# 2. allow users to join the event with !bomb join, for a cost of 50 points (do not start if there is only one player)
# 3. create a json with a rng'd wire # and each participating user (because i don't know how else to do this using multithreading)
# 4. each user (in a defined order) will then choose to cut a wire using !cutwire <#>. 
# 5. if that wire was the one rng'd earlier, they "blow up" and are eliminated from the event. time out users if they take too long
# 6. repeat steps 3 - 5 until only one user remains
# 7. the winner will receive 200 + the amount paid by all users that joined the event (tentative to change)
#
# the json will contain a dictionary with the bad wire and each user and the wire they've chosen that round
# we want to keep information on which users are still "in" every round and which wires are still available
# as of right now, i don't know of any other ways to store this information in a json, but i'm sure there's a much better way


# preserve turn order (1, 2, 3 (3 loses) ---> 4, 1, 2)


# at the start of the round, inform players of the turn order
# inform players when it's their turn and which wires they can choose from


file_string = 'bomb_info.json'
active_player_pos = 1



def rng(upper: int) -> int:
	# we'll never want to rng into wire 0 (since that's unintuitive for users)
	return random.randint(1, upper)


def join(user: str):
	bomb_dict = util.load_file(file_string)
	bomb_dict[user] = 0
	util.write_file(file_string, temp_dict)


def start():
	temp_dict = {'bad_wire': 0}
	util.write_file(file_string, temp_dict)


def choose_wire(player: str, num: int) -> str:
	bomb_dict = util.load_file(file_string)
	if num == bomb_dict['bad_wire']:
		bomb_dict.pop(player)
		util.write_file(file_string, bomb_dict)
		if active_player_pos > len(bomb_dict) -1:
			active_player_pos -= len(bomb_dict) -1
		return f'{player} blew up the bomb! cmonBruh'
	else:
		bomb_dict[player] = num
		util.write_file(file_string, bomb_dict)
		active_player_pos += 1
		if active_player_pos > len(bomb_dict) - 1:
			active_player_pos -= len(bomb_dict) -1
		return f'{player} lives! Clap'


def new_round() -> str:
	# returns true if there will be a new round and false if only one user remains
	bomb_dict = util.load_file(file_string)
	if len(bomb_dict) == 2:
		winner = get_players[0]
		points.change_points(winner, 300, '+')
		return f'{winner} is the last man standing and has won 300 points!'
	else:
		bomb_dict = {x: 0 for x in bomb_dict} # resets all values to 0
		bomb_dict['bad_wire'] = rng(len(bomb_dict) - 1)
		util.write_file(file_string, bomb_dict)
		return f'{get_players[active_player_pos]}, you\'re up next. Cut one of these wires with !bomb cut: {bomb_squad.get_avail_wires()}'


def elim_player(player: str):
	bomb_dict = util.load_file(file_string)
	choose_wire(player, bomb_dict['bad_wire'])


def cleanup():
	if os.path.exists(file_string):
		os.remove(file_string)


def get_avail_wires() -> list:
	bomb_dict = util.load_file(file_string)

	# the second argument of range() is exclusive. so range(1, 10) produces numbers 1 - 9
	# bomb_dict will have all users + bad_wire
	# instead of doing len(bomb_dict) - 1 after pop('bad_wire'), we reverse it
	avail_wires = list(range(1, len(bomb_dict)))
	bomb_dict.pop('bad_wire')
	chosen_wires = list(bomb_dict.values())

	# for every wire in avail_wires, if they are not in chosen_wires, add them to this list
	return [wire for wire in avail_wires if wire not in chosen_wires]


def get_players() -> list:
	bomb_dict = util.load_file(file_string)
	bomb_dict.pop('bad_wire')
	return bomb_dict.keys()


def get_active_player() -> str:
	players = get_players()
	return players[active_player_pos]


def get_idle(user: str) -> int:
	# returns true if a player hasn't made a choice yet and vice-versa
	bomb_dict = util.load_file(file_string)
	return bomb_dict[user] != 0


def is_alive() -> bool:
	# this is mainly used to make sure that two instances of this event can't happen at the same time
	return os.path.exists(file_string)


def in_progress() -> bool:
	bomb_dict = util.load_file(file_string)
	return bomb_dict['value'] != 0