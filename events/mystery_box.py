from numpy import random

class MysteryBox:
    def __init__(self):
        self.active = False
        self.top_bidder = ''
        self.box_points = 0
        self.top_bid = 0

    def activate(self):
        self.active = True
        self.box_points = self.box_rng()
        print( f'[box] spawned with {self.box_points:,} points')

    def box_rng(self) -> int:
        return int(random.gamma(2,400))

    def bid(self, player: str, bid: int):
        self.top_bidder = player
        self.top_bid = bid

    def get_box_details(self) -> (str,int,int):
        # winner, points, bid
        return self.top_bidder, self.box_points, self.top_bid

    def cleanup(self):
        self.active = False
        self.box_points = 0
        self.top_bidder = ''
        self.top_bid = 0
