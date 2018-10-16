import sys
import json
import points
import random


file_text = 'lottery_info.json'
init_val = 500
max_ticket_number = 5000


def load_file() -> [dict]:
	with open(file_text) as file:
		return json.load(file)


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


def get_remaining_tickets() -> [int]:
	lottery_dict = load_file()
	return max_ticket_number - len(lottery_dict) + 1 # len(lottery_dict) while empty is 1 because of value


def user_exists_check(user: [str]) -> [bool]:
	lottery_dict = load_file()
	owners_list = lottery_dict.values()
	return user in owners_list


def ticket_exists_check(number: [int], lottery_dict: [dict]) -> [bool]:
# checks if a ticket exists in our db
	# lottery_dict = load_file()
	return str(number) in lottery_dict


def generate_ticket(lottery_dict: [dict]) -> [int]:
	ticket = random.randint(1, max_ticket_number)
	while ticket_exists_check(ticket, lottery_dict):
		ticket = random.randint(1, max_ticket_number)
	return ticket


def buy_ticket(user: [str], qty: [int]):
# buys tickets for a user and increases lottery pot
	lottery_dict = load_file()
	for x in range(qty):
		lottery_dict[str(generate_ticket(lottery_dict))] = user
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
		clean_tickets()


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
