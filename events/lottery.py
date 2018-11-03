import points
import utilities as util


file_string = 'json/lottery_info.json'
init_val = 1000
max_ticket_number = 5000



def get_value() -> int:
# returns the lottery pot
	lottery_dict = util.load_file(file_string)
	return lottery_dict['value']


def get_tickets(user: str) -> int:
# returns the number of tickets owned by a user
	lottery_dict = util.load_file(file_string)
	owners_list = list(lottery_dict.values())
	tickets = 0
	for x in range(len(owners_list)):
		if owners_list[x] == user:
			tickets += 1
	return tickets


def get_remaining_tickets() -> int:
	lottery_dict = util.load_file(file_string)
	return max_ticket_number - len(lottery_dict) + 1 # len(lottery_dict) while empty is 1 because of value


def user_exists_check(user: str) -> bool:
	lottery_dict = util.load_file(file_string)
	owners_list = lottery_dict.values()
	return user in owners_list


def ticket_exists_check(number: int, lottery_dict: dict) -> bool:
# checks if a ticket exists in our db
	# lottery_dict = load_file()
	return str(number) in lottery_dict


def generate_ticket(lottery_dict: dict) -> int:
	ticket = util.rng(1, max_ticket_number)
	while ticket_exists_check(ticket, lottery_dict):
		ticket = util.rng(1, max_ticket_number)
	return ticket


def buy_ticket(user: str, qty: int):
# buys tickets for a user and increases lottery pot
	lottery_dict = util.load_file(file_string)
	for x in range(qty):
		lottery_dict[str(generate_ticket(lottery_dict))] = user
	lottery_dict['value'] += qty * 5
	util.write_file(file_string, lottery_dict)


def draw() -> str:
# json stores the tickets as strings instead of ints
	winning_ticket = str(util.rng(1, max_ticket_number))
	lottery_dict = util.load_file(file_string)
	if winning_ticket in lottery_dict:
		winner = lottery_dict[winning_ticket]
		points.change_points(winner, lottery_dict['value'], '+')
		return winner
	else:
		clean_tickets()


def clean_tickets():
# clears all the tickets after a draw
	lottery_dict = util.load_file(file_string)
	lottery_value = lottery_dict['value']
	new_dict = {'value': lottery_value}
	util.write_file(file_string, new_dict)


def cleanup():
# starts a new lottery after a win
	new_dict = {'value': init_val}
	util.write_file(file_string, new_dict)
