import operator
import utilities as util
from gaybot import User

file_string = 'json/users.json'

class Points:
    def __init__(self):
        self.users = util.pickle_load(file_string) # keys = usernames: values = username objects


    def check_user_exists(self, username: str) -> bool:
        return username in self.users


    def add_user(self, username: str):
        self.users[username] = User()


    def remove_user(self, username: str):
        self.users.pop(username, None)


    def get_points(self, username: str) -> int:
        if not self.check_user_exists(username):
            if viewer in util.get_viewers() and viewer not in util.load_blacklist():
                self.add_user(username)
        return self.users[username].points


    def get_richest(self) -> [tuple]:
    # returns a list containing all users sorted from richest to poorest
    # each user is itself a tuple with tuple[0] being the username and tuple[1] being the user object
    # tuple[0][0] returns the username with the richest points
    # tuple[0][1] returns the user object of the richest user
        return sorted(list(self.users.items()), key=lambda x: x[1].points, reverse=True)
        

    def update_points(self, viewers = util.get_viewers()):
        for v in viewers:
            if v in util.load_blacklist():
                continue
            if v not in self.users:
                self.add_user(v)
            else:
                self.users[v].points += self.users[v].income


    def change_points(self, username: str, points: int, op: str):
        # op takes in "+", "-", ...
        ops = {"+": operator.iadd,
               "-": operator.isub,
               "*": operator.imul,
               "/": operator.ifloordiv}
        update_set = {username}
        if username in util.everyone:
            viewers = util.get_viewers()
            blacklist = util.load_blacklist()
            update_set.update({v for v in viewers if v not in blacklist})
        for viewer in update_set:
            if not self.check_user_exists(username):
                if viewer in util.get_viewers() and viewer not in util.load_blacklist():
                    self.add_user(username)
            self.users[viewer].points = ops[op](self.users[viewer].points, points)


    def set_points(self, username: str, points: int):
        update_set = {username}
        if username in util.everyone:
            viewers = util.get_viewers()
            blacklist = util.load_blacklist()
            update_set.update({v for v in viewers if v not in blacklist})
        for viewer in update_set:
            if not self.check_user_exists(username):
                if viewer in util.get_viewers() and viewer not in util.load_blacklist():
                    self.add_user(username)            
            self.users[viewer].points = points


    def save(self):
        util.pickle_write(file_string, self.users)
