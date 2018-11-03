import points
import utilities as util
from numpy import random

file_string = 'json/box_info.json'



def box_rng() -> int:
    return int(random.gamma(2, 400))


def spawn():
	box_dict = {
		"box_points": 0,
    	"top_bidder": "",
    	"top_bid": 0
	}

	box_dict["box_points"] = box_rng()
	util.write_file(file_string, box_dict)
	print ('[box] spawned with ' + format(box_dict["box_points"], ',d') + ' points')


def cleanup():
	util.remove_file(file_string)


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
	return util.file_exists(file_string)