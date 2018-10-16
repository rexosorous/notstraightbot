import sys
import json
import points
import random


file_text = 'lottery_info.json'
init_val = 500
max_ticket_number = 1000


def load_file() -> [dict]:
	with open(file_text) as file:
		lottery_dict = json.load(file)
	return lottery_dict


def get_value() -> [int]:
# returns the lottery pot
	lottery_dict = load_file()
	return lottery_dict['value']


def get_tickets(user: [str]) -> [int]:
# returns the number of tickets owned by a user
	lottery_dict = load_file()
	owners_list = list(lottery_dict.values())
	tickets = 0
	for x in range(len(owners_list)):
		if owners_list[x] == user:
			tickets += 1
	return tickets


def ticket_exists_check(number: [int]) -> [bool]:
# checks if a ticket exists in our db
	lottery_dict = load_file()
	if str(number) in lottery_dict:
		return True
	else:
		return False


def user_exists_check(user: [str]) -> [bool]:
	lottery_dict = load_file()
	owners_list = lottery_dict.values()
	if user in owners_list:
		return True
	else:
		return False


def generate_ticket() -> [int]:
	ticket = random.randint(1, max_ticket_number)
	while ticket_exists_check(ticket):
		ticket = random.randint(1, max_ticket_number)
	return ticket


def buy_ticket(user: [str], qty: [int]):
# buys tickets for a user and increases lottery pot
	lottery_dict = load_file()
	for x in range(qty):
		lottery_dict[generate_ticket()] = user
		with open(file_text, 'w') as file:
			json.dump(lottery_dict, file, indent=4)
	lottery_dict['value'] += qty * 5
	with open(file_text, 'w') as file:
		json.dump(lottery_dict, file, indent=4)


def draw() -> [str]:
# json stores the tickets as strings instead of ints
	winning_ticket = str(random.randint(1, max_ticket_number))
	lottery_dict = load_file()
	if winning_ticket in lottery_dict:
		winner = lottery_dict[winning_ticket]
		points.add_points(winner, lottery_dict['value'])
		return winner
	else:
		print('loser')
		clean_tickets()
		return ''


def clean_tickets():
# clears all the tickets after a draw
	lottery_dict = load_file()
	lottery_value = lottery_dict['value']
	new_dict = {'value': lottery_value}
	with open(file_text, 'w') as file:
		json.dump(new_dict, file, indent=4)


def cleanup():
# starts a new lottery after a win
	new_dict = {'value': init_val}
	with open(file_text, 'w') as file:
		json.dump(new_dict, file, indent=4)
