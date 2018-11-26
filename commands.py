import threading

import utilities as util
import redeem

currency = 'GayBux'



# custom exceptions
class AdminError(Exception): # raised when a non-admin user attempts to use admin commands
    pass

class BalanceError(Exception): # raised when a user has insufficient funds to perform an action
    pass

class IllegalValueError(Exception): # raised when a user attempts to use negative poitns for an action
    pass



class Commands:
    def __init__(self, user: str, args: [str], points, events):
        self.user = user
        self.args = args # a list of each word in the command
        self.arg_count = len(self.args)
        self.points = points
        self.events = events
        self.blacklist = util.load_blacklist()


    def execute(self) -> str:
        cmds = {
            'help': [self.help, 'shows a list of commands', '!help <category>'],
            'commands': [self.help, 'shows a list of commands', '!help <category>'],

            'emotes': [self.emote_list, 'shows all the bttv emotes enabled on this channel', '!bttvemotes'],
            'emoteslist': [self.emote_list, 'shows all the bttv emotes enabled on this channel', '!bttvemotes'],
            'bttvemotes': [self.emote_list, 'shows all the bttv emotes enabled on this channel', '!bttvemotes'],

            'admins': [self.admin_list, 'shows all the bot admins', '!admins'],
            'adminlist': [self.admin_list, 'shows all the bot admins', '!admins'],
            'adminslist': [self.admin_list, 'shows all the bot admins', '!admins'],

            'banlist': [self.ban_list, 'shows all the users banned from this bot', '!banlist'],
            'banned': [self.ban_list, 'shows all the users banned from this bot', '!banlist'],

            'eventlist': [self.event_list, 'shows all the events for this bot', '!eventlist'],

            'ban': [self.ban, 'bans a user from this bot', '!ban <user>'],

            'unban': [self.unban, 'unbans a user from this bot', '!unban <user>'],

            'space': [self.space_out, 'inserts spaces between every character in the phrase it\'s given', '!spaceout <text>'],
            'spaceout': [self.space_out, 'inserts spaces between every character in the phrase it\'s given', '!spaceout <text>'],

            'memetext': [self.meme_text, 'capitalizes every other letter in the phrase it\'s given', '!memetext <text>'],
            'spongetext': [self.meme_text, 'capitalizes every other letter in the phrase it\'s given', '!memetext <text>'],
            'spongebobtext': [self.meme_text, 'capitalizes every other letter in the phrase it\'s given', '!memetext <text>'],

            'discord': [self.discord, 'gives the link to the channel\'s discord', '!discord'],

            'weather': [self.weather, 'shows cortana\'s monologue if you\'re bad at bridgefall', '!weather'],

            'points': [self.check_points, f'shows how much {currency} a user has', '!points <user>'],
            'gaybux': [self.check_points, f'shows how much {currency} a user has', '!points <user>'],

            'addpoints': [self.add_points, f'adds {currency} to a user', '!addpoints <user> <amount>'],

            'subpoints': [self.sub_points, f'subtracts {currency} from a user', '!subpoints <user> <amount>'],
            'removepoints': [self.sub_points, f'subtracts {currency} from a user', '!subpoints <user> <amount>'],
            'deletepoints': [self.sub_points, f'subtracts {currency} from a user', '!subpoints <user> <amount>'],

            'multpoints': [self.mult_points, f'multiplies a user\'s {currency} balance', '!multpoints <user> <amount>'],
            'multiplypoints': [self.mult_points, f'multiplies a user\'s {currency} balance', '!multpoints <user> <amount>'],

            'divpoints': [self.div_points, f'divides a user\'s {currency} balance', '!divpoints <user> <amount>'],
            'dividepoints': [self.div_points, f'divides a user\'s {currency} balance', '!divpoints <user> <amount>'],

            'setpoints': [self.set_points, f'sets a user\'s {currency} balance', '!setpoints <user> <amount>'],

            'givepoints': [self.give_points, f'gives some of your {currency} to another user', '!givepoints <user> <amount>'],
            'givegaybux': [self.give_points, f'gives some of your {currency} to another user', '!givepoints <user> <amount>'],
            'givebux': [self.give_points, f'gives some of your {currency} to another user', '!givepoints <user> <amount>'],

            'gamble': [self.gamble, 'rolls a number between 0 and 100. if it\'s < 50, you lose what you bet. if it\'s 50, you don\'t win or lose anything. if it\'s > 50, you win what you bet. if it\'s 100, you win double what you bet', '!gamble <amount>'],

            'admingamble': [self.admin_gamble, 'gambles, but always guarantees a roll of 100', '!admingamble <amount>'],

            'redeem': [self.redeem, f'rewards cost 1000 {currency} each. here is a list of all the rewards: {", ".join(redeem.rewards)}', '!redeem <reward>'],

            'luck': [self.check_luck, 'shows how lucky someone is when they gamble', '!luck <user>'],

            'setluck': [self.set_luck, 'sets a user\'s luck value', '!setluck <user> <amount>'],

            'addluck': [self.add_luck, 'adds to a user\'s luck value', '!addluck <user> <amount>'],

            'subluck': [self.sub_luck, 'subtracts from a user\'s luck value', '!subluck <user> <amount>'],

            'income': [self.check_income, f'shows how many {currency} a user makes every 15 seconds', '!income <user>'],

            'setincome': [self.set_income, 'sets a user\'s income', '!setincome <user> <amount>'],

            'payraise': [self.add_income, 'adds to a user\'s income', '!payraise <user> <amount>'],
            'addincome': [self.add_income, 'adds to a user\'s income', '!payraise <user> <amount>'],

            'paycut': [self.sub_income, 'subtracts from a user\'s income', '!paycut <user> <amount>'],
            'subincome': [self.sub_income, 'subtracts from a user\'s income', '!paycut <user> <amount>'],

            'event': [self.spawn_event, 'spawns an event', '!event <event name>'],
            'spawnevent': [self.spawn_event, 'spawns an event', '!event <event name>'],
            'spawn': [self.spawn_event, 'spawns an event', '!event <event name>'],

            'bid': [self.bid, f'bids on a mystery {currency} box', '!bid <amount>'],

            'topbid': [self.check_bid, f'shows what the highest bid is for the mystery {currency} box', '!topbid'],
            'highestbid': [self.check_bid, f'shows what the highest bid is for the mystery {currency} box', '!topbid'],

            'lotto': [self.check_lottery, 'shows how much the lottery is currently worth', '!lotto'],
            'lottery': [self.check_lottery, 'shows how much the lottery is currently worth', '!lotto'],
            'checklotto': [self.check_lottery, 'shows how much the lottery is currently worth', '!lotto'],
            'checklottery': [self.check_lottery, 'shows how much the lottery is currently worth', '!lotto'],

            'buytickets': [self.buy_tickets, 'buys some lottery tickets', '!buytix <amount>'],
            'buytix': [self.buy_tickets, 'buys some lottery tickets', '!buytix <amount>'],

            'tickets': [self.check_tickets, 'checks how many lottery tickets you have', '!tix'],
            'tix': [self.check_tickets, 'checks how many lottery tickets you have', '!tix'],
        }

        if self.user in self.blacklist:
            return f'{user} is banned from this bot'

        try:
            if self.args[0] in cmds:
                if self.arg_count > 1:
                    if self.args[1] in ['info', 'help']:
                        return cmds[self.args[0]][1]
                    if self.args[1] == 'syntax':
                        return cmds[self.args[0]][2]
                return cmds[self.args[0]][0]()
            return 'that command does not exist'
        except IndexError:
            return 'incorrect command syntax'
        except ValueError:
            return 'please use integers'
        except KeyError:
            return 'that user is banned from this bot'
        except AdminError:
            return 'you must be an admin to do that'
        except BalanceError:
            return 'you have insufficient funds'
        except IllegalValueError:
            return 'you can\'t use negative numbers'
        except:
            return 'unknown error'




###########################################################################################
######################################### UTILITY #########################################
###########################################################################################

    def balance(self, username: str) -> str:
    # condenses code so i don't have to type line below all the time
        return f'{username} now has {self.points.get_points(username):,} {currency}'


    def point_converter(self, username: str, val) -> int:
    # converts user input into an int if possible
    # raises an error if the user is trying to use a negative number or if the user doesn't have enough points
        if val == 'all':
            self.args[1] = self.points.get_points(username)
        val = int(self.args[1])

        if val < 1:
            raise IllegalValueError
        if val > self.points.get_points(username):
            raise BalanceError

        return val




###########################################################################################
########################################## BASIC ##########################################
###########################################################################################

    def help(self):
        help_dict = {
            'admin': ['!ban', '!unban', '!addpoints', '!subpoints', '!multpoints', '!divpoints', '!setpoints', '!admingamble', '!luck', '!setluck', '!addluck', '!subluck', '!setincome', '!addincome', '!subincome', '!event'], 
            'basic': ['!bttvemotes', '!admins', '!banlist', '!eventlist''!spaceout', '!memetext', '!discord', '!weather'],
            'points': ['!points', '!givepoints', '!gamble', '!redeem', '!income'], 
            'mysterybox': ['!bid', '!topbid'], 
            'lottery': ['!lotto', '!tix', '!buytix']}

        if self.arg_count == 1:
            return f'type "info" or "syntax" after any command to learn more about it. here is a list of all help commands: !help {", !help ".join(help_dict.keys())}'
        if self.args[1] not in help_dict.keys():
            return 'that help command does not exist'

        return f'here is a list of all {self.args[1]} commands: !help {", ".join(help_dict[self.args[1]])}'


    def emote_list(self):
        return 'EZ  Clap  HYPERCLAP  SPANK  SPANKED  FeelsGoldMan'


    def admin_list(self):
        return f'list of bot admins: {", ".join(util.admins)}'


    def ban_list(self):
        return f'list of users banned from this bot: {", ".join(self.blacklist)}'


    def event_list(self):
        return f'list of bot events: mystery {currency} box, lottery'


    def ban(self):
        if self.user not in util.admins:
            raise AdminError

        target = util.word_fixer(self.args[1])

        if target in self.blacklist:
            return 'that user is already banned'
        if target in util.admins:
            return 'cannot ban bot admins'

        self.blacklist.append(target)
        self.points.remove_user(target)
        util.write_blacklist(self.blacklist)
        return f'{target} has been banned from this bot'


    def unban(self):
        if self.user not in util.admins:
            raise AdminError

        target = util.word_fixer(self.args[1])

        if target not in self.blacklist:
            return 'that user is not currently banned'

        self.blacklist.remove(target)
        util.write_blacklist(self.blacklist)
        return f'{target} has been unbanned from this bot'


    def space_out(self):
    # converts 'hello world' to 'h e l l o w o r l d'
        return ' '.join(''.join(self.args[1:]))


    def meme_text(self):
    # converts 'hello world' to 'hElLo WoRlD'
        meme_string = '' # python strings are immutable so we can't edit them directly
        cbool = False # true = make uppercase

        for char in ' '.join(self.args[1:]):
            meme_string += char.upper() if cbool else char # add the char to meme_string
            if char.isalpha(): # alternates capilization, ONLY if the character is a letter (not spaces or numbers)
                cbool = not cbool

        return meme_string


    def discord(self):
        return 'join the discord server! https://discord.gg/f4bzBXJ'


    def weather(self):
        return 'Interesting. The weather patterns here seem natural and not artificial. I wonder if the rings\' environment systems are malfunctioning. Or if the designers wanted the installation to have inclement weather.'




###########################################################################################
######################################### POINTS ##########################################
###########################################################################################

    def check_points(self):
        username = self.user if self.arg_count == 1 else util.word_fixer(self.args[1])

        if username in ['top', 'richest']:
            top = self.points.get_richest()
            return f'{top[0][0]} is the richest with {top[0][1].points:,} {currency}! POGGERS'
        elif username in['bottom', 'bot', 'poorest']:
            bot = self.points.get_richest()
            return f'{bot[len(bot)-1][0]} is the poorest with {bot[len(bot)-1][1].points:,} {currency}. PressF'

        return f'{username} has {self.points.get_points(username):,} {currency}'


    def add_points(self):
        if self.user not in util.admins: # only allow admins to use this command
            raise AdminError

        username = util.word_fixer(self.args[1])
        add = int(self.args[2])
        self.points.change_points(username, add, '+')
        return f'everyone has been given {add:,} {currency}! Kreygasm' if username in util.everyone else \
               self.balance(username)


    def sub_points(self):
        if self.user not in util.admins: # only allow admins to use this command
            raise AdminError

        username = util.word_fixer(self.args[1])

        if self.args[2] == 'all': # allow someone to have all their points subtracted from them
           self.args[2] = self.points.get_points(username)

        sub = int(self.args[2])
        self.points.change_points(username, sub, '-')
        return f'everyone has lost {sub * -1:,} {currency}. FeelsBadMan' if username in util.everyone else \
               self.balance(username)


    def mult_points(self):
        if self.user not in util.admins: # only allow admins to use this command
            raise AdminError

        username = util.word_fixer(self.args[1])
        mult = int(self.args[2])
        self.points.change_points(username, mult, '*')
        return f'everyone has had their {currency} multiplied by {mult}! Kreygasm' if username in util.everyone else \
               self.balance(username)


    def div_points(self):
        if self.user not in util.admins: # only allow admins to use this command
            raise AdminError

        username = util.word_fixer(self.args[1])
        div = int(self.args[2])
        self.points.change_points(username, div, '*')
        return f'everyone has had their {currency} divided by {div}! FeelsBadMan' if username in util.everyone else \
               self.balance(username)


    def set_points(self):
        if self.user not in util.admins: # only allow admins to use this command
            raise AdminError

        username = util.word_fixer(self.args[1])
        val = int(self.args[2])
        self.points.change_points(username, val, '*')
        return f'everyone has had their {currency} set to {val}.' if username in util.everyone else \
               self.balance(username)


    def give_points(self):
        donator = self.user
        recipient = util.word_fixer(self.args[1])

        val = self.point_converter(donator, self.args[2])

        self.points.change_points(donator, val, '-')
        self.points.change_points(recipient, val, '+')

        return f'{self.balance(donator)} && {self.balance(recipient)}'


    def gamble(self):
        val = self.point_converter(self.user, self.args[1])
        result = util.rng(self.points.users[self.user].luck, 100)

        if result < 50:
            self.points.change_points(self.user, val, '-')
            return f'{self.user} rolled a {result} and has lost {val:,} {currency}! you now have {self.points.get_points(self.user):,} {currency}.'
        elif result == 50:
            return f'{self.user} rolled a {result} and has tied! you have not won or lost any {currency}.'
        elif result > 50 and result < 100:
            self.points.change_points(self.user, val, '+')
            return f'{self.user} rolled a {result} and has won {val:,} {currency}! you now have {self.points.get_points(self.user):,} {currency}.'
        elif result == 100:
            self.points.change_points(self.user, val * 2, '+')
            return f'{self.user} rolled a {result}! JACKPOT! you have won {val * 2:,} {currency}! you now have {self.points.get_points(self.user):,} {currency}.'


    def admin_gamble(self):
        if self.user not in util.admins:
            raise AdminError

        val = int(self.args[1]) * 2
        self.points.change_points(self.user, val, '+')
        return f'{self.user} rolled a 100! JACKPOT! you have won {val:,} {currency}! you now have {self.points.get_points(self.user):,} {currency}.'


    def redeem(self):
        if self.args[1] not in redeem.rewards:
            return 'that reward does not exist'
        if self.points.get_points(self.user) < 1000:
            raise BalanceError

        self.points.change_points(self.user, 1000, '-')
        redeem_thread = threading.Thread(target=redeem.play_sound, args=(self.args[1],))
        redeem_thread.daemon = True
        redeem_thread.start()

        return f'redeeming reward...'


    def check_luck(self):
        if self.user not in util.admins:
            raise AdminError

        username = util.word_fixer(self.args[1])
        return f'{username} has {self.points.users[username].luck} luck'


    def set_luck(self):
        if self.user not in util.admins:
            raise AdminError

        username = util.word_fixer(self.args[1])
        new_luck = int(self.args[2])
        self.points.users[username].luck = new_luck
        return f'{username} now has {new_luck} luck'


    def add_luck(self):
        if self.user not in util.admins:
            raise AdminError

        username = util.word_fixer(self.args[1])
        add_luck = int(self.args[2])
        self.points.users[username].luck += add_luck
        return f'{username} now has {self.points.users[username].luck} luck'


    def sub_luck(self):
        if self.user not in util.admins:
            raise AdminError

        username = util.word_fixer(self.args[1])
        sub_luck = int(self.args[2])
        self.points.users[username].luck -= sub_luck
        return f'{username} now has {self.points.users[username].luck} luck'


    def check_income(self):
        username = self.user if self.arg_count == 1 else util.word_fixer(self.args[1])
        return f'{username} has an income of {self.points.users[username].income:,} {currency}/15s'


    def set_income(self):
        if self.user not in util.admins:
            raise AdminError
        
        username = util.word_fixer(self.args[1])
        new_income = int(self.args[2])
        self.points.users[username].income = new_income
        return f'{username} now has an income of {new_income:,} {currency}/15s'


    def add_income(self):
        if self.user not in util.admins:
            raise AdminError
        
        username = util.word_fixer(self.args[1])
        add_income = int(self.args[2])
        self.points.users[username].income += add_income
        return f'{username} now has an income of {self.points.users[username].income:,} {currency}/15s'


    def sub_income(self):
        if self.user not in util.admins:
            raise AdminError
        
        username = util.word_fixer(self.args[1])
        sub_income = int(self.args[2])
        self.points.users[username].income += sub_income
        return f'{username} now has an income of {self.points.users[username].income:,} {currency}/15s'




###########################################################################################
##################################### EVENTS GENERAL ######################################
###########################################################################################

    def spawn_event(self):
        if self.args[1] not in self.events.spawn_dict:
            return 'there are no events with that name'
        self.events.start_event(self.args[1])
        return f'spawning {self.args[1]}'





###########################################################################################
####################################### MYSTERY BOX #######################################
###########################################################################################

    def bid(self):
        if not self.events.box.active:
            return 'a mystery box hasn\'t spawned yet'

        if self.arg_count == 1:
            return self.check_bid()
        
        bid = self.point_converter(self.user, self.args[1])
        top_bid = self.events.box.top_bid
        top_bidder = self.events.box.top_bidder

        if bid > top_bid:
            if top_bidder:
                self.points.change_points(top_bidder, top_bid, '+') # return points to the previous top bidder if one exists
            self.points.change_points(self.user, bid, '-')
            self.events.box.bid(self.user, bid)
            return f'{self.user} now has the highest bid with {bid:,} {currency}'
        return 'your bid is not high enough'


    def check_bid(self):
        if not self.events.box.active:
            return 'a mystery box hasn\'t spawned yet'
        return f'the top bid is {self.events.box.top_bid:,} {currency} by {self.events.box.top_bidder}. use !bid <# of {currency}> to place your bid!'




###########################################################################################
######################################### LOTTERY #########################################
###########################################################################################

    def check_lottery(self):
        return f'the lottery is at {self.events.lottery.get_value():,} {currency}! buy a ticket with !buytickets <# of tickets> for 5 {currency} each!'


    def buy_tickets(self):
        qty = int(self.args[1])
        cost = self.point_converter(self.user, qty * 5)

        if qty > self.events.lottery.get_remaining_tickets(): # if the user wants to buy more tickets than are available, give them what's left
            qty = self.events.lottery.get_remaining_tickets()
            cost = qty * 5

        self.points.change_points(self.user, cost, '-')
        self.events.lottery.buy_tickets(self.user, qty)

        return f'{self.user} now has {self.events.lottery.get_tickets(self.user):,} lottery tickets.'


    def check_tickets(self):
        username = self.user if self.arg_count == 1 else util.word_fixer(self.args[1])
        return f'{username} has {self.events.lottery.get_tickets(self.user):,} lottery tickets.'