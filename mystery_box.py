import numpy
import json
import os

import points
import utilities as util

file_string = 'box_info.json'



def rng(min_value: int, max_value: int) -> int:
    return int(numpy.random.gamma(2, 400))


def spawn():
	box_dict = {
		"box_points": 0,
    	"top_bidder": "",
    	"top_bid": 0
	}

	box_dict["box_points"] = rng(0, 1000)
	util.write_file(file_string, box_dict)
	print ('[box] spawned with ' + format(box_dict["box_points"], ',d') + ' points')


def cleanup():
	if os.path.exists(file_string):
		os.remove(file_string)


def bid(user: str, bid: int):
	box_dict = util.load_file(file_string)

	if box_dict["top_bidder"] != '':
		points.change_points(box_dict["top_bidder"], box_dict["top_bid"], '+')
	box_dict["top_bidder"] = user
	box_dict["top_bid"] = bid
	points.change_points(box_dict["top_bidder"], box_dict["top_bid"] * -1, '+')
	util.write_file(file_string, box_dict)


def get_top_bidder() -> str:
	box_dict = util.load_file(file_string)
	return box_dict["top_bidder"]


def get_top_bid() -> int:
	box_dict = util.load_file(file_string)
	return box_dict["top_bid"]


def get_box_points() -> int:
	box_dict = util.load_file(file_string)
	return box_dict["box_points"]


def is_alive() -> bool:
	return os.path.exists(file_string)
