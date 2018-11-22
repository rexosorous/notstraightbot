import sys
import irc.bot
import requests
import threading
import json
# import queue
from time import sleep

# my own libraries
import points
import utilities as util
import redeem
import stats

# placed all the event modules in their own folder
import events.mystery_box as mystery_box
import events.lottery as lottery
# import events.bomb_squad as bomb_squad



############ TO DO #################

# Poll
# play (youtube link to song)
# 
# POINTS RELATED COMMANDS
# trivia
# betting
#   a. pick a number - fixed buy in and winner (closest to #) wins the whole pot
#   b. horse race
#   c. mario party - https://www.youtube.com/watch?v=GXTRNSuC_YQ
#   d. russian roulette
#   e. don't pop the balloon
# challenge

# REEDEM POINTS FOR
# control music
# text to speech

# abstract away messaging to util so that other modules can message
# make variable names consistent: events should have 'players' not 'users'
# find a better way to display commands when user types !help
# users can guarantee a win on lottery by buying max tickets and they'll always make a profit, find some way to balance this


# bomb_q = queue.Queue()


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel


        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print (f'Connecting to {server} on port {port}...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)


        self.blacklist = util.load_blacklist()
        self.points = points.Points()
        self.mystery_box = mystery_box.MysteryBox(self.points)
        self.lottery = lottery.Lottery(self.points)
        self.stats = stats.Stats()


    def message(self, output: str):
        self.connection.privmsg(self.channel, output)


    def update_points(self):
        while True:
            self.points.update_points()
            self.points.save()
            sleep(15)

   
    def event_timer(self):
        time_min = 15 # in minutes
        time_max = 30 # in minutes
        while True:
            sleep(util.rng(time_min * 60, time_max * 60)) # sleep(x) sleeps for x seconds
            event_number = util.rng(1, 2)
            if event_number == 1:
                self.mystery_box_event()
            elif event_number == 2:
                self.lottery_event()


    def mystery_box_event(self):
        if not self.mystery_box.is_alive():
            self.mystery_box.activate()
            self.message('A Mystery Points Box has spawned! Type !bid <#> to try to win it! The auction will end in 3 minutes.')
            sleep(60)
            self.message('2 minutes left to bid on the Mystery Points Box!')
            sleep(60)
            self.message('1 minute left to bid on the Mystery Points Box!')
            sleep(30)
            self.message('30 seconds left to bid on the Mystery Points Box!')
            sleep(20)
            self.message('10 seconds left to bid on the Mystery Points Box!')
            sleep(10)

            if self.mystery_box.get_top_bidder() == '':
                self.message('the box disappears, saddened that no one bid on it BibleThump')
                print ('[box] despawned with no winners')
            else:
                winner, box_points, bid = self.mystery_box.get_box_details()
                self.points.change_points(winner, box_points, '+')

                self.message(f'{winner} has won the mystery box with a bid of {bid:,} points! Congratulations!')
                self.message(f'The box contained {self.mystery_box.get_box_points():,} points! {winner} now has {self.points.get_points(winner):,} points.')
                print (f'[box] {winner} has won the box')

            self.mystery_box.cleanup()


    def lottery_event(self):
        print ('[lottery] is being drawn')
        self.message('The winning lottery ticket will be drawn in 1 minute! Buy your tickets for 5 points with !buytickets <qty>.')
        sleep(60)
        winner = self.lottery.draw()
        self.message('The winning lottery ticket has been drawn and...')
        sleep(3)
        if winner:
            self.message(f'{winner} won the lottery! You won {self.lottery.get_value():,} points, giving you {self.points.get_points(winner):,} points total! EZ Clap')
            self.lottery.cleanup()
            print (f'[lottery] {winner} won the lottery')
        else:
            self.message('Nobody won the lottery PepeREE')
            print ('[lottery] no winners')


    # def bomb_event(self):
    #     if not bomb_squad.is_alive():
    #         print ('[bomb] starting')
    #         bomb_squad.start()
    #         self.message('Calling all bomb squad technicians, there\'s a bomb at the orphanage! You\'ll have one minute to join this event with !bomb join')
    #         sleep(60)
    #         if not bomb_squad.new_round():
    #             print('[bomb] not enough players to start')
    #             self.message('There aren\'t enough players to start the event.')
    #             bomb_squad.cleanup()


    # def bomb_timer(self, active_player: str):
    #     bomb_thread = threading.Thread(target=self.bomb_timeout, args=[active_player])
    #     bomb_thread.daemon = True
    #     bomb_thread.start()
        # i can use queue module instead of writing to json files https://pymotw.com/2/Queue/
        # so instead of having to write to json files to make sure all my threads are using the same data, i can use queues


    # def bomb_timeout(self, active_player: str):
    #     # if after 15 seconds a player hasn't made a choice, eliminate them from the game
    #     sleep(15)
    #     try:
    #         temp = bomb_q.get()
    #     except Queue.Empty:
    #         self.message(f'{active_player}, you waited too long and the bomb blew up on you!')
    #         bomb_squad.elim_player(active_player)

 

    # checks if a user exists in our db
    def user_exists_check(self, user: str) -> bool:
        if self.points.check_user_exists(user):
            return True
        else:
            self.message(f'cannot find {user}')
            return False


    # checks for illegal numbers
    def illegal_value_check(self, value: int) -> bool:
        try:
            number = int(value)
            if number < 1:
                self.message('only non-zero positive numbers are allowed')
                return False
        except ValueError:
            self.message(f'{value} is not a number')
            return False

        return True


    # checks if a user has enough points
    def funds_check(self, user: str, value: int) -> bool:
        if int(value) > self.points.get_points(user):
            self.message('you have insufficient funds')
            return False
        else:
            return True


    # checks if:
    # a user exists in our database
    # a user has enough points to do an action
    # the points is not a negative number
    def points_check(self, user: str, value: int) -> bool:
        if self.user_exists_check(user):
            if self.illegal_value_check(value):
                if self.funds_check(user, value):
                    return True
        return False



    # returns a string with a user's current points value
    def user_balance(self, user: str) -> str:
        rstring = f'{user} now has {self.points.get_points(user):,} points'
        return rstring


    def add_user(self, user: str) -> bool:
        if user in self.blacklist:
            self.message(f'{user} is banned from this bot.')
            return
        if not self.points.check_user_exists(user):
            chat = util.get_viewers()
            if user in chat:
                self.points.add_user(user)
                return True
            else:
                self.message(f'{user} is not in chat.')
                return False
        else:
            return True


    def syntax(self, cmd_raw: str):
        syntax_dict = util.load_file('json/commands_syntax.json')
        self.message(syntax_dict[cmd_raw])



























    def on_welcome(self, c, e):
        print ('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

        self.message('bot is live')

        points_thread = threading.Thread(target=self.update_points)
        points_thread.daemon = True
        points_thread.start()

        event_thread = threading.Thread(target=self.event_timer)
        event_thread.daemon = True
        event_thread.start()


    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd_raw = e.arguments[0][1:]
            print ('[' + e.source[:e.source.find('!')] + '] ' + cmd_raw)
            self.do_command(e, cmd_raw)


    def do_command(self, e, cmd_raw):
        args = cmd_raw.split(' ')
        args_full = ' '.join(args[1:])
        cmd_raw = cmd_raw.lower()
        cmd = args[0].lower()
        user = e.source[:e.source.find('!')] # the user who sent the message


        ############ SPECIAL COMMANDS ###################
        # list all the commands
        if user in self.blacklist:
            self.message(f'{user} is banned from this bot')
            return

        if cmd_raw in ['help', 'commands', 'commandslist']:
            help_list = []
            output_string = 'Commoner available commands: '
            common_commands_file = open('json/commands.json', "r")
            common_commands_list_full = [line.strip() for line in common_commands_file]
            common_commands_file.close()
            for common_commands in common_commands_list_full:
                parsed_command = common_commands.split('::')
                if parsed_command[1] == 'admin' and user in util.admins:
                    help_list.append('!' + parsed_command[0])
                    output_string = 'Admin available commands: '
                elif parsed_command[1] == 'common':
                    help_list.append('!' + parsed_command[0])
            self.message(output_string + ', '.join(help_list))


        # list all the admins with a () around their name to avoid pinging them
        elif cmd_raw in ['admin', 'admins', 'adminlist', 'adminslist']:
            admin_list = []
            for admin in util.admins:
                admin_list.append('(' + admin + ')')
            self.message('List of Admins: ' + ', '.join(admin_list))


        # list all bttv emotes
        elif cmd_raw in ['bttvemotes', 'emotes', 'emoteslist']:
            self.message('EZ  Clap  HYPERCLAP  SPANK  SPANKED  FeelsGoldMan')


        # add new commands
        elif cmd in ['newcommand', 'addcommand', 'createcommand'] and user in util.admins:
            if len(args) < 4 or args[2].lower() not in ['admin', 'common']:
                self.syntax(cmd)
            else:
                # remove the ! at the beginning of the new command name if present
                new_name = util.word_fixer(args[1])
                common_commands_list = util.get_commands_list()
                if new_name in common_commands_list:
                    self.message(new_name + ' command already exists')

                # add the new command
                else: 
                    common_commands_file_write = open(commands_file_string, "a")
                    new_permission = util.word_fixer(args[2])
                    common_commands_file_write.write('\n' + new_name + '::' + new_permission + '::')
                    for a in range(3, len(args)):
                        common_commands_file_write.write(args[a] + ' ')
                    print(f'{user} created {new_name} command.')
                    self.message(f'Successfully created {new_name} command')
                    common_commands_file_write.close()


        #remove commands
        elif cmd in ['deletecommand', 'removecommand'] and user in util.admins:
            # make sure the command has the correct syntax
            if len(args) != 2:
                self.syntax(cmd)
            else: 
                # remove ! at the beginning of the command name if present
                name = util.word_fixer(args[1])

                # store commands.json in replace
                # edit replace
                # re-write commands.json with edited replace
                replace = []
                common_commands_list = util.get_commands_list()
                if name in common_commands_list: 
                    for common_commands in common_commands_list_full:
                        parsed_command = common_commands.split('::')
                        if name != parsed_command[0]:
                            replace.append(common_commands)
                    else:
                        common_commands_fileWrite = open(commands_file_string, "w")
                        common_commands_fileWrite.write(replace[0])
                        for replacements in range(1, len(replace)):
                            common_commands_fileWrite.write('\n' + replace[replacements])
                        common_commands_fileWrite.close()
                        print(f'{user} deleted {name} command.')
                        self.message(f'Successfully deleted {name} command')
                else:
                    self.message(f'{name} command does not exist')


        elif cmd == 'ban' and user in util.admins:
            if len(args) != 2:
                self.syntax(cmd)
            else:
                target = util.word_fixer(args[1])
                if target not in util.admins:
                    if target in self.blacklist:
                        self.message('that user is already banned')
                    else:
                        self.blacklist.append(target)
                        self.points.remove_user(target)
                        util.write_blacklist(self.blacklist)
                        self.message(f'{target} has been banned from this bot')

        elif cmd == 'unban' and user in util.admins:
            if len(args) != 2:
                self.sytnax(cmd)
            else:
                target = util.word_fixer(args[1])
                if target not in self.blacklist:
                    self.message('that user was not already banned')
                else:
                    self.blacklist.remove(target)
                    util.write_blacklist(self.blacklist)
                    self.message(f'{target} has been unbanned from this bot')



        # converts 'hello world' to 'h e l l o w o r l d'
        elif cmd in ['space', 'spaceout']:
            self.message(' '.join(args_full))



        # converts 'hello world' to 'HeLlO wOrLd'
        elif cmd in ['memetext', 'spongebobtext']:
            meme_string = '' # python strings are immutable so we can't edit args_full directly
            cbool = True if args_full[0].isupper() else False # controls pattern of text
                # "Text" becomes "TeXt" and "text" becomes "tExT"
                # True = upper
                # False = lower

            for char in args_full.lower():
                meme_string += char.upper() if cbool else char # capitalize a character of cbool is true
                if char.isalpha(): # makes sure that 'don't' becomes 'DoN't' and not 'DoN'T'
                    cbool = not cbool

            self.message(meme_string)











        ########## POINTS RELATED COMMANDS ##############
        # check the points of users
        elif cmd == 'points':
            if len(args) == 1:
                if self.add_user(user):
                    self.message(f'{user} has {self.points.get_points(user):,} points')
            elif len(args) == 2:
                username = util.word_fixer(args[1])

                if username in ['top', 'richest']:
                    top = self.points.get_bot()
                    self.message(f'{top[len(top)-1][0]} is the richest with {top[len(top)-1][1]:,} points! POGGERS')
                elif username in['bottom', 'bot', 'poorest']:
                    bot = self.points.get_bot()
                    self.message(f'{bot[0][0]} is the poorest with {bot[0][1]:,} points. PressF')
                else:
                    if self.add_user(username):
                        self.message(f'{username} has {self.points.get_points(username):,} points')
            else:
                self.syntax(cmd)


        # add points to users
        elif cmd == 'addpoints' and user in util.admins:
            if len(args) != 3:
                self.syntax(cmd)
            else:
                username = util.word_fixer(args[1])

                try:
                    add = int(args[2])
                    if username in util.everyone:
                        self.points.change_points(username, add, '+')
                        self.message(f'everyone has been given {add:,} points! Kreygasm')                    
                    elif self.add_user(username):
                        self.points.change_points(username, add, '+')
                        self.message(self.user_balance(username))
                except ValueError:
                    self.message(args[2] + ' is not a number')                       


        # subtract points from users
        elif cmd in ['subpoints', 'removepoints', 'deletepoints'] and user in util.admins:
            if len(args) != 3:
                self.syntax(cmd)
            else:
                username = util.word_fixer(args[1])

                if args[2].lower() == 'all':
                        args[2] = self.points.get_points(username)

                try:
                    sub = int(args[2])
                    if username in util.everyone:
                        self.points.change_points(username, sub, '-')
                        self.message(f'everyone has lost {sub * -1:,} points. FeelsBadMan')            
                    elif self.add_user(username):
                        self.points.change_points(username, sub, '-')
                        self.message(self.user_balance(username))
                except ValueError:
                    self.message(args[2] + ' is not a number')


        elif cmd == 'setpoints' and user in util.admins:
            if len(args) != 3:
                self.syntax(cmd)
            else:
                username = util.word_fixer(args[1])

                try:
                    value = int(args[2])
                    if username in util.everyone:
                        self.points.set_points(username, value)
                        self.message(f'everyone has had their points reset to {value:,} points.')
                    elif self.add_user(username):
                        self.points.set_points(username, value)
                        self.message(self.user_balance(username))
                except ValueError:
                    self.message(args[2] + ' is not a number')



        elif cmd in ['multpoints', 'multiplypoints']:
            if len(args) != 3:
                self.syntax(cmd)
            else:
                username = util.word_fixer(args[1])

                if username in util.everyone:
                    if self.illegal_value_check(args[2]):
                        multiplier = int(args[2])
                        self.points.change_points(username, multiplier, '*')
                        self.message(f'everyone has had their points multiplied by {multiplier}! Kreygasm')
                elif self.user_exists_check(username):
                    if self.illegal_value_check(args[2]):
                        multiplier = int(args[2])
                        self.points.change_points(username, multiplier, '*')
                        self.message(self.user_balance(username))



        elif cmd in ['divpoints', 'dividepoints']:
            if len(args) != 3:
                self.syntax(cmd)
            else:
                username = util.word_fixer(args[1])

                if username in util.everyone:
                    if self.illegal_value_check(args[2]):
                        multiplier = int(args[2])
                        self.points.change_points(username, multiplier, '/')
                        self.message(f'everyone has had their points divided by {multiplier}. FeelsBadMan')
                elif self.user_exists_check(username):
                    if self.illegal_value_check(args[2]):
                        multiplier = int(args[2])
                        self.points.change_points(username, multiplier, '/')
                        self.message(self.user_balance(username))






        # allow users to give or donate their points
        elif cmd in ['givepoints', 'donatepoints']:
            if len(args) != 3:
                self.syntax(cmd)
            else:
                donator = util.word_fixer(user)
                recipient = util.word_fixer(args[1])

                if args[2].lower() == 'all':
                    args[2] = self.points.get_points(donator)

                if self.points_check(donator, args[2]):
                    if (self.user_exists_check(recipient)):
                        value = int(args[2])
                        self.points.donate_points(donator, recipient, value)
                        self.message(self.user_balance(donator) + ' && ' + self.user_balance(recipient))



        # allow players to gamble their points
        # generate a number from 0 to 100
        # if <50, player loses
        # if >50, player wins
        # if =50, no change
        # if =100, player wins double. jackpot!
        elif cmd == 'gamble':
            if len(args) != 2:
                self.syntax(cmd)
            else:
                if args[1].lower() == 'all':
                    args[1] = self.points.get_points(user)
                if self.points_check(user, args[1]):
                    value = int(args[1])
                    result = util.rng(0, 100)
                    if result < 50:
                        self.points.change_points(user, value, '-')
                        self.message(f'{user} rolled a {result} and has lost {value:,} points! you now have {self.points.get_points(user):,} points.')
                    elif result > 50 and result < 100:
                        self.points.change_points(user, value, '+')
                        self.message(f'{user} rolled a {result} and has won {value:,} points! you now have {self.points.get_points(user):,} points.')
                    elif result == 100:
                        self.points.change_points(user, value * 2, '+')
                        self.message(f'{user} rolled a {result}! JACKPOT! you have won {value * 2:,} points! you now have {self.points.get_points(user):,} points.')
                    elif result == 50:
                        self.message(f'{user} rolled a {result} and has tied! you have not won or lost any points.')


        # guarantees a 100 every time
        elif cmd == 'admingamble' and user in util.admins:
            if len(args) != 2:
                self.syntax(cmd)
            else:
                if args[1].lower() == 'all':
                    args[1] = self.points.get_points(user)
                if self.points_check(user, args[1]):
                    value = int(args[1])
                    result = 100
                    self.points.change_points(user, value * 2, '+')
                    self.message(f'{user} rolled a {result}! JACKPOT! you have won {value * 2:,} points! you now have {self.points.get_points(user):,} points.')


        # bidding for mystery points box
        elif cmd == 'bid':
            if len(args) != 2:
                self.syntax(cmd)
            elif not self.mystery_box.is_alive():
                self.message('A mystery points box hasn\'t spawned yet')
            else:
                if args[1].lower() == 'all':
                    args[1] = self.points.get_points(user)
                
                if self.points_check(user, args[1]):
                    value = int(args[1])
                    if value > self.mystery_box.get_top_bid():
                        self.mystery_box.bid(user, value)
                        self.message(f'{self.mystery_box.get_top_bidder()} now has the highest bid with {self.mystery_box.get_top_bid():,} points!')
                    else:
                        self.message(f'{user} your bid is not high enough')


        elif cmd in ['beatbid', 'beattopbid', 'beathighestbid']:
            if len(args) != 2:
                self.syntax(cmd)
            elif not self.mystery_box.is_alive():
                self.message('A mystery points box hasn\'t spawned yet')
            else:
                if self.points_check(user, args[1]):
                    value = int(args[1]) + self.mystery_box.get_top_bid()
                    if self.funds_check(user, value):
                        self.mystery_box.bid(user, value)
                        self.message(f'{self.mystery_box.get_top_bidder()} now has the highest bid with {self.mystery_box.get_top_bid():,} points!')


        elif cmd_raw in ['topbid', 'highestbid']:
            if not self.mystery_box.is_alive():
                self.message('A mystery points box hasn\'t spawned yet')
            else: 
                self.message(f'The top bid is {self.mystery_box.get_top_bid():,} points by {self.mystery_box.get_top_bidder()}')









        elif cmd_raw in ['lottery', 'lotto', 'checklotto', 'checklottery']:
            self.message(f'The lottery is at {self.lottery.get_value():,} points! Buy a ticket with !buytickets <# of tickets> for 5 points each!')


        elif cmd in ['buytickets', 'buyticket', 'buytix']:
            if len(args) != 2:
                self.syntax(cmd)
            else:
                if self.illegal_value_check(args[1]):
                    qty = int(args[1])
                    cost = qty * 5
                    if self.points_check(user, cost):
                        if qty > self.lottery.get_remaining_tickets():
                            self.message(f"There aren't enough tickets. There are only {self.lottery.get_remaining_tickets():,} tickets left. WutFace")
                        else:
                            self.lottery.buy_ticket(user, qty)
                            self.message(f'{user} now has {self.lottery.get_tickets(user):,} lottery tickets.')


        elif cmd in ['tickets', 'ticket', 'tix']:
            if len(args) == 1:
                username = user
            elif len(args) == 2:
                username = util.word_fixer(args[1])
            else:
                syntax(cmd)

            if len(args) in [1, 2]:
                if self.lottery.user_exists_check(username):
                    self.message(f'{username} has {self.lottery.get_tickets(username):,} lottery tickets.')
                else:
                    self.message(f'{username} has 0 lottery tickets.')


        # elif cmd_raw in ['bomb', 'bombsquad']:
        #     if bomb_squad.is_alive():
        #         if len(args) == 1:
        #             self.message(f'Remaining players: {bomb_squad.get_players()}')
        #         elif len(args) == 2:
        #             arg = util.word_fixer(args[1])
        #             if arg =='join':
        #                 if not bomb_squad.in_progress():
        #                     bomb_squad.join(user)
        #                     self.message(f'{user} has joined the bomb squad event')
        #                 else:
        #                     self.message('The bomb squad event has already started.')

        #     else:
        #         self.message('The bomb squad event hasn\'t started yet.') 


        # elif cmd in ['cut', 'cutwire']:
        #     if len(args) == 2:
        #         if user == bomb_squad.get_active_player():
        #             wire_num = util.word_fixer(args[2])
        #             if illegal_value_check(wire_num):
        #                 wire_num = int(wire_num)
        #                 if wire_num in bomb_squad.get_avail_wires():
        #                     self.message(f'{user} cuts wire #{wire_num} and...')
        #                     sleep(3)
        #                     self.message(bomb_squad.choose_wire(user, wire_num))
        #                 else:
        #                     self.message('You can\'t cut that wire.')
        #         else:
        #             self.message(f'It\'s {bomb_squad.get_active_player()}\'s turn, not yours.')
        #     else:
        #         syntax(cmd)












            # else:
            #       arg = util.word_fixer(args[1])
            #       if arg == 'join':
            #           if len(args) == 2:
            #               if not bomb_squad.in_progress():
            #                   bomb_squad.join(user)
            #               else:
            #                   self.message('The bomb squad event is already in progress')
            #       elif arg in ['cut', 'select', 'cutwire', 'selectwire']:
            #           if len(args) == 3:
            #               if user == bomb_squad.get_active_player():
            #                   wire_num = util.word_fixer(args[2]) # we want to let users type !bomb cut #2
            #                   if illegal_value_check(wire_num):
            #                       wire_num = int(wire_num)
            #                       if wire_num in bomb_squad.get_avail_wires():
            #                           self.message(f'{user} cuts wire #{wire_num} and...')
            #                           sleep(3)
            #                           if bomb_squad.choose_wire(user, wire_num):
            #                               self.message(f'{user} lives! Clap')
            #                               self.message(f'{bomb_squad.get_active_player()}, you\'re up next. Cut one of these wires with !bomb cut: {bomb_squad.get_avail_wires()}')
            #                               bomb_timeout(bomb_squad.get_active_player())
            #                           else:
            #                               self.message(f'{user} blew up the bomb! cmonBruh')
            #                               if not new_round():
            #                                   self.message(f'{bomb_squad.get_players()} is the last man standing and won ') # figure out how many points to pay out
            #                                   bomb_squad.cleanup()
            #                               else:
            #                                   self.message(f'There\'s another bomb! {bomb_squad.get_active_player()}, you\'re up next. Cut one of these wires with !bomb cut: {bomb_squad.get_avail_wires()}')
            #                                   bomb_timeout(bomb_squad.get_active_player())
            #                       else:
            #                           self.message('That wire has already been cut.')
            #               else:
            #                   self.message(f'{user}, it\'s not your turn.')


















        # allow admins to spawn events
        elif cmd in ['event', 'spawnevent', 'spawn'] and user in util.admins:
            if len(args) != 2:
                self.syntax(cmd)
            else:
                event_name = args[1]
                if event_name.lower() in ['box', 'mysterybox', 'mysterypointsbox']:
                    event_thread = threading.Thread(target=self.mystery_box_event)
                    event_thread.daemon = True
                    event_thread.start()
                elif event_name.lower() in ['lottery', 'lotto']:
                    event_thread = threading.Thread(target=self.lottery_event)
                    event_thread.daemon = True
                    event_thread.start()



















        ########################### REDEEM POINTS #########################
        elif cmd in ['redeem', 'redeempoints']:
            rewards = ['dejavu', '90s', 'gas', 'spacejam', 'countryroads', 'fitnessgram', 'skeleton', 'victoryell']
            if len(args) > 2:
                self.message('Syntax for that command is: !redeem <reward>. Type \"!redeem help\" for more info')
            elif len(args) == 1:
                rewards_list = ', '.join(rewards)
                    self.message(f'rewards cost 1000 points each. here is a list of all the rewards: {rewards_list}')
            else:
                arg = args[1]
                if arg == 'help':
                    rewards_list = ', '.join(rewards)
                    self.message(f'rewards cost 1000 points each. here is a list of all the rewards: {rewards_list}')
                else:
                    if self.funds_check(user, 1000):
                        self.points.change_points(user, 1000, '-')
                        redeem_thread = threading.Thread(target=redeem.play_sound, args=(arg,))
                        redeem_thread.daemon = True
                        redeem_thread.start()






        ########################### STATS ###############################
        # !stat list
        # !stat keyesbump
        # !stat keyesbump success
        # !removestat keyesbump fail

        elif cmd in ['stat', 'stats']:
            if len(args) == 2:
                if args[1] in ['list', 'tricks', 'trickslist', 'all']:
                    self.message(f'here\'s a list of all the tricks i keep stats for: {self.stats.get_tricks()}')
                else:
                    self.message(self.stats.get_stat(args[1]))
            if len(args) == 3:
                if args[2] not in ['success', 'fail', 'failure']:
                    self.message('the second argument for this command must be \'success\' or \'fail\'')
                self.message(self.stats.change_stat(args[1], args[2], '+'))

        elif cmd in ['removestat', 'statremove']:
            if len(args) != 3:
                self.syntax(cmd)
            else:
                if args[2] not in ['success', 'fail', 'failure']:
                    self.message('the second argument for this command must be \'success\' or \'fail\'')
                self.message(self.stats.change_stat(args[1], args[2], '-'))















        ################# BASIC TEXT COMMANDS ######################
        else:
            common_commands_file = open('json/commands.json', "r")
            common_commands_list_full = [line.strip() for line in common_commands_file]
            common_commands_file.close()

            for common_commands in common_commands_list_full:
                parsed_command = common_commands.split('::')
                command_name = parsed_command[0]
                permission = parsed_command[1]
                output = parsed_command[2]

                if cmd_raw == command_name:
                    # admin commands
                    if permission == 'admin':
                        if user in util.admins:
                            self.message(output)
                        else:
                            self.message(f"I'm afraid I can't let you do that, {user}")
                    # common commands
                    elif permission == 'common':
                        self.message(output)






def main():
    # if len(sys.argv) != 5:
    #     print("Usage: twitchbot <username> <client id> <token> <channel>")
    #     sys.exit(1)

    # username  = sys.argv[1]
    # client_id = sys.argv[2]
    # token     = sys.argv[3]
    # channel   = sys.argv[4]

    username = 'Gay_Bot'
    client_id = 'idgnrmfdwlmb2b4wldetuzewc6s1kd'
    token = 'o46q25lvzkat7ifntm8ndv9urbsjra'
    channel = 'gay_zach'

    util.remove_file('json/box_info.json')

    try:
        bot = TwitchBot(username, client_id, token, channel)
        bot.start()
    except KeyboardInterrupt:
        bot.message('bot has committed honorable sudoku')
        bot.points.save()
        bot.lottery.save()
        bot.stats.save()
    except:
        bot.message('someone murdered me.')
        bot.points.save()
        bot.lottery.save()
        bot.stats.save()
        raise

if __name__ == "__main__":
    main()