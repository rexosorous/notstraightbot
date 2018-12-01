import threading
from time import sleep

import events.mystery_box as mystery_box
import events.lottery as lottery

currency = 'GayBux'

class BotEvents:
    def __init__(self, connection, channel, points):
        self.box = mystery_box.MysteryBox()
        self.lottery = lottery.Lottery()
        self.points = points

        self.connection = connection
        self.channel = channel

        self.spawn_dict = {
            'box': self.start_box,
            'mysterybox': self.start_box,
            'mysterypointsbox': self.start_box,
            'lotto': self.start_lottery,
            'lottery': self.start_lottery
        }


    def message(self, output: str):
        self.connection.privmsg(self.channel, output)


    def start_event(self, event_name: str):
        event_thread = threading.Thread(target=self.spawn_dict[event_name])
        event_thread.daemon = True
        event_thread.start()


    def start_box(self):
        if not self.box.active:
            self.box.activate()
            self.message(f'A Mystery {currency} Box has spawned! Type !bid <#> to try to win it! The auction will end in 3 minutes.')
            sleep(60)
            self.message(f'2 minutes left to bid on the Mystery {currency} Box!')
            sleep(60)
            self.message(f'1 minute left to bid on the Mystery {currency} Box!')
            sleep(30)
            self.message(f'30 seconds left to bid on the Mystery {currency} Box!')
            sleep(20)
            self.message(f'10 seconds left to bid on the Mystery {currency} Box!')
            sleep(10)

            if not self.box.top_bidder:
                self.message('the box disappears, saddened that no one bid on it BibleThump')
                print ('[box] despawned with no winners')
            else:
                winner, box_points, bid = self.box.get_box_details()
                self.points.change_points(winner, box_points, '+')

                self.message(f'{winner} has won the mystery box with a bid of {bid:,} {currency}! Congratulations!')
                self.message(f'the box contained {self.box.box_points:,} {currency}! {winner} now has {self.points.get_points(winner):,} points.')
                print (f'[box] {winner} has won the box')

            self.box.cleanup()


    def start_lottery(self):
        print ('[lottery] is being drawn')
        self.message(f'The winning lottery ticket will be drawn in 1 minute! Buy your tickets for 5 {currency} with !buytickets <qty>.')
        sleep(60)
        winner = self.lottery.draw()
        self.message('The winning lottery ticket has been drawn and...')
        sleep(3)
        if winner:
            self.points.change_points(winner, self.lottery.get_value(), '+')
            self.points.users[winner].luck += 5
            self.message(f'{winner} won the lottery! you won {self.lottery.get_value():,} {currency} and 5 luck for gambling! EZ Clap')
            self.lottery.cleanup()
            print (f'[lottery] {winner} won the lottery')
        else:
            self.message('Nobody won the lottery PepeREE')
            print ('[lottery] no winners')