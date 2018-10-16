import sys
import points
import numpy
import json
import os

file_string = 'box_info.json'


def load_file() -> [dict]:
	with open(file_string) as file:
		box_dict = json.load(file)
	return box_dict


def rng(min_value: [int], max_value: [int]) -> [int]:
    output = int(numpy.random.gamma(2, 400))
    return output

def spawn():
	box_dict = {
		"box_points": 0,
    	"alive": 0,
    	"top_bidder": "",
    	"top_bid": 0
	}

	box_dict["box_points"] = rng(0, 1000)
	box_dict["alive"] = 1
	with open(file_string, 'w') as file:
		json.dump(box_dict, file, indent=4)
	print ('[box] spawned with ' + format(box_dict["box_points"], ',d') + ' points')

def despawn():
	box_dict = load_file()
	box_dict["alive"] = 0

	with open(file_string, 'w') as file:
		json.dump(box_dict, file, indent=4)

def cleanup():
	if os.path.exists(file_string):
		os.remove(file_string)

def bid(user: [str], bid: [int]):
	box_dict = load_file()

	if box_dict["top_bidder"] != '':
		points.add_points(box_dict["top_bidder"], box_dict["top_bid"])
	box_dict["top_bidder"] = user
	box_dict["top_bid"] = bid
	points.add_points(box_dict["top_bidder"], box_dict["top_bid"] * -1)

	with open(file_string, 'w') as file:
		json.dump(box_dict, file, indent=4)

def get_top_bidder() -> [str]:
	box_dict = load_file()
	return box_dict["top_bidder"]

def get_top_bid() -> [int]:
	box_dict = load_file()
	return box_dict["top_bid"]

def get_box_points() -> [int]:
	box_dict = load_file()
	return box_dict["box_points"]

def is_alive() -> [bool]:
	if os.path.exists(file_string):
		with open(file_string) as file:
			box_dict = json.load(file)
		if box_dict["alive"] == 0:
			return False
		elif box_dict["alive"] == 1:
			return True
	else:
		return False