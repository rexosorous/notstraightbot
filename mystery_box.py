import sys
import points
import numpy
import json
import os

file_string = 'box_info.json'


def load_file() -> [dict]:
	with open(file_string) as file:
		return json.load(file)


def write_file(box_dict: [dict]):
	with open(file_string, 'w') as file:
		json.dump(box_dict, file, indent=4)


def rng(min_value: [int], max_value: [int]) -> [int]:
    return int(numpy.random.gamma(2, 400))


def spawn():
	box_dict = {
		"box_points": 0,
    	"top_bidder": "",
    	"top_bid": 0
	}

	box_dict["box_points"] = rng(0, 1000)
	write_file(box_dict)
	print ('[box] spawned with ' + format(box_dict["box_points"], ',d') + ' points')


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
	write_file(box_dict)


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
	return os.path.exists(file_string)
