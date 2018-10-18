import sys
import json
import random
import os
import points

# UNRELATED NOTES bc i won't remember unless it's in here
# users can guarantee a win on lottery by buying max tickets and they'll always make a profit, find some way to balance this
# should it be possible for more than one event (not the same one) to happen at the same time?
# make variable names consistent: events should have 'players' not 'users'
# restructure event commands


# it's late and i wanted to work on this, but i don't want to think too hard
# so anywhere it says 'unsure', it's because i didn't want to put the effort into figuring it out yet.
# future me will figure it out

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


# should the turn order be:
#	1. first place shifts over every round (1, 2, 3 (3 loses) ---> 2, 4, 1)
#	2. preserve turn order (1, 2, 3 (3 loses) ---> 4, 1, 2)


# at the start of the round, inform players of the turn order
# inform players when it's their turn and which wires they can choose from


file_string = 'bomb_info.json'


def load_file() -> dict:
	with open(file_string) as file:
		return json.load(file)


def write_file(bomb_dict: dict):
	with open(file_string, 'w') as file:
		json.dump(bomb_dict, file, indent=4)


def append_file(bomb_dict: dict):
	with open(file_string, 'a') as file:
		json.dump(bomb_dict, file, indent=4)


def rng(upper: int) -> int:
	# we'll never want to rng into wire 0 (since that's unintuitive for users)
	return random.randint(1, upper)


def join(user: str):
	temp_dict = {user: 0}
	append_file(temp_dict)
	# unsure if i can append a dict to my json. especially if a dict already exists in there


def start():
	temp_dict = {'bad_wire': 0}
	write_file(temp_dict)


def choose_wire(user: str, num: int) -> bool:
	# returns true if user lived and false if user dieded
	bomb_dict = load_file()
	if num == bomb_dict['bad_wire']:
		bomb_dict.pop(user)
		write_file(bomb_dict)
		return False
	else:
		bomb_dict[user] = num
		write_file(bomb_dict)
		return True


def new_round() -> bool:
	# returns true if there will be a new round and false if only one user remains
	bomb_dict = load_file()
	if len(bomb_dict) == 2:
		return False
	else:
		bomb_dict = {x: 0 for x in bomb_dict} # resets all values to 0
		bomb_dict['bad_wire'] = rng(len(bomb_dict) - 1)
		write_file(bomb_dict)
		return True


def cleanup():
	if os.path.exists(file_string):
		os.remove(file_string)


def get_active_player() -> str:
	# logic here
	return


def get_avail_wires() -> list:
	bomb_dict = load_file()

	# the second argument of range() is exclusive. so range(1, 10) produces numbers 1 - 9
	# bomb_dict will have all users + bad_wire
	# instead of doing len(bomb_dict) - 1 after pop('bad_wire'), we reverse it
	avail_wires = list(range(1, len(bomb_dict)))
	bomb_dict.pop('bad_wire')
	chosen_wires = bomb_dict.values()

	# unsure if "for chosen_wires in avail_wires" would work
	for x in chosen_wires:
		if chosen_wires[x] in avail_wires:
			avail_wires.remove(chosen_wires[x])
	return avail_wires


def get_players() -> list:
	bomb_dict = load_file()
	bomb_dict.pop('bad_wire')
	return bomb_dict.keys()


def get_idle(user: str) -> int:
	# returns true if a player hasn't made a choice yet and vice-versa
	bomb_dict = load_file()
	if bomb_dict[user] == 0:
		return False
	else:
		return True

	# return False if bomb_dict == 0 else return True
	# would the above work?


def is_alive() -> bool:
	# can't think of a better function name right now
	# this is mainly used to make sure that two instances of this event can't happen at the same time
	return os.path.exists(file_string)


def in_progress() -> bool:
	bomb_dict = load_file()
	if bomb_dict['value'] == 0:
		return False
	else:
		return True