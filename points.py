import requests
import operator
from time import sleep

import utilities as util

file_string = 'json/points_table.json'

class Points:
    def __init__(self):
        self.points_dict = util.load_file(file_string)

    def check_user_exists(self, user: str) -> bool:
        return user in self.points_dict

    def remove_user(self, user: str):
        self.points_dict.pop(user, None)

    def get_points(self, user: str):
        return self.points_dict[user]

    def get_bot(self) -> list:
        return sorted(self.points_dict.items(), key=lambda kv: kv[1])

    def update_points(self, usernames = util.get_viewers()):
        for user in usernames:
            if user in util.load_blacklist():
                continue
            if user not in self.points_dict:
                self.points_dict[user] = 100
            elif user in util.admins:
                self.points_dict[user] += 3
            else:
                self.points_dict[user] += 1

    def change_points(self, user: str, points: int, op: str):
        # op takes in "+", "-", ...
        ops = {"+": operator.iadd,
               "-": operator.isub,
               "*": operator.imul,
               "/": operator.ifloordiv}
        update_set = {user}
        if user in util.everyone:
            viewers = util.get_viewers()
            blacklist = util.load_blacklist()
            update_set.update({v for v in viewers if v not in blacklist})
        for viewer in update_set:
            self.points_dict[viewer] = ops[op](self.points_dict[viewer], points)

    def set_points(self, user: str, points: int):
        update_set = {user}
        if user in util.everyone:
            viewers = util.get_viewers()
            blacklist = util.load_blacklist()
            update_set.update({v for v in viewers if v not in blacklist})
        for viewer in update_set:
            self.points_dict[viewer] = points

    def save(self):
        util.write_file(file_string, self.points_dict)
