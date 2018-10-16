import sys
import irc.bot
import requests
import threading
import random
import json
from time import sleep

# my own libraries
import points
import mystery_box
import lottery


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
# lottery - contains all the points lost to the lottery
#   a. let users choose a number
#   b. default to giving them a random number
#   c. allow users to buy more than one ticket

# REEDEM POINTS FOR
# control music
# messages appear in chat
# text to speech


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
        print ('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)


    def message(self, output: [str]):
        self.connection.privmsg(self.channel, output)

   
    def event_timer(self):
        time_min = 30 # in minutes
        time_max = 45 # in minutes
        while True:
            sleep(rng(time_min * 60, time_max * 60))
            event_number = rng(1, 2)
            if event_number == 1:
                self.mystery_box_event()
            elif event_number == 2:
                self.lottery_event()


    def mystery_box_event(self):
        if not mystery_box.is_alive():
            mystery_box.spawn()
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
            mystery_box.despawn()

            if mystery_box.get_top_bidder() == '':
                self.message('the box disappears, saddened that no one bid on it BibleThump')
                print ('[box] despawned with no winners')
                mystery_box.cleanup()
            else:
                winner = mystery_box.get_top_bidder()
                bid = mystery_box.get_top_bid()
                box_points = mystery_box.get_box_points()

                points.add_points(winner, box_points)

                self.message(winner + ' has won the mystery box with a bid of ' + format(bid, ',d') + ' points! Congratulations!')
                self.message('The box contained ' + format(mystery_box.get_box_points(), ',d') + ' points! ' 
                    + winner + ' now has ' + format(points.get_points(winner), ',d') + ' points.')
                print ('[box] ' + winner + ' has won the box')

                mystery_box.cleanup()


    def lottery_event(self):
        print ('[lottery] is being drawn')
        self.message('The winning lottery ticket will be drawn in 1 minute! Buy your tickets for 5 points with !buytickets <qty>.')
        sleep(6)
        winner = lottery.draw()
        self.message('The winning lottery ticket has been drawn and...')
        sleep(3)
        if winner == '':
            self.message('Nobody won the lottery PepeREE')
            print ('[lottery] no winners')
        else:
            self.message(winner + ' won the lottery! You won ' + format(lottery.get_value(), ',d') + ' points, giving you ' + 
        sleep(3)
        if winner:
           self.message(winner + ' won the lottery! You won ' + format(lottery.get_value(), ',d') + ' points, giving you ' + 
                format(points.get_points(winner), ',d') + ' points total! EZ Clap'))
            lottery.cleanup()
            print ('[lottery] ' + winner + ' won the lottery')
        else:
            self.message('Nobody won the lottery PepeREE')
            print ('[lottery] no winners')
 

    # checks if a user exists in our db
    def user_exists_check(self, user: [str]) -> [bool]:
        if points.user_exists_check(user):
            return True
        else:
            self.message('cannot find ' + user)
            return False


    # checks for illegal numbers
    def illegal_value_check(self, value: [int]) -> [bool]:
        clean = True

        try:
            number = int(value)
            if number < 1:
                clean = False
                self.message('only non-zero positive numbers are allowed')
        except ValueError:
            clean = False
            self.message(value + ' is not a number')

        return clean


    # checks if a user has enough points
    def funds_check(self, user: [str], value: [int]) -> [bool]:
        if int(value) > points.get_points(user):
            self.message('you have insufficient funds')
            return False

        else:
            return True


    # checks if:
    # a user exists in our database
    # a user has enough points to do an action
    # the points is not a negative number
    def points_check(self, user: [str], value: [int]) -> [bool]:
        if self.user_exists_check(user):
            if self.illegal_value_check(value):
                if self.funds_check(user, value):
                    return True
        return False



    # returns a string with a user's current points value
    def user_balance(self, user: [str]) -> [str]:
        rstring = (user + ' now has ' + format(points.get_points(user), ',d') + ' points')
        return rstring


    def add_user(self, user: [str]) -> [bool]:
        if not points.user_exists_check(user):
            chat = points.get_viewers()
            if user in chat and user != 'skinnyseahorse' and user != 'notstraightbot':
                points.add_user(user)
                return True
            else:
                self.message(user + ' is not in chat')
                return False
        else:
            return True


    def syntax(self, cmd_whole: [str]):
        with open('commands_syntax.json') as syntax_file:
            syntax_dict = json.load(syntax_file)
        self.message(syntax_dict[cmd_whole])



























    def on_welcome(self, c, e):
        print ('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

        self.message('bot is live')

        event_thread = threading.Thread(target=self.event_timer)
        event_thread.daemon = True
        event_thread.start()

    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd_whole = e.arguments[0][1:]
            print ('[' + e.source[:e.source.find('!')] + '] ' + cmd_whole)
            self.do_command(e, cmd_whole)


    def do_command(self, e, cmd_whole):
        c = self.connection
        admins = {'gay_zach', 'hwangbroxd'}

        cmd_whole = cmd_whole.lower()
        arguments = cmd_whole.split(' ')
        cmd = arguments[0]
        user = e.source[:e.source.find('!')] # the user who sent the message


        ############ SPECIAL COMMANDS ###################
        # list all the commands
        if cmd_whole in ['help', 'commands', 'commandslist']:
            help_list = []
            output_string = 'Commoner available commands: '
            common_commands_file = open('commands.json', "r")
            common_commands_list_full = [line.strip() for line in common_commands_file]
            common_commands_file.close()
            for common_commands in common_commands_list_full:
                parsed_command = common_commands.split('::')
                if parsed_command[1] == 'admin' and user in admins:
                    help_list.append('!' + parsed_command[0])
                    output_string = 'Admin available commands: '
                elif parsed_command[1] == 'common':
                    help_list.append('!' + parsed_command[0])
            # c.privmsg(self.channel, output_string + ', '.join(help_list))
            self.message(output_string + ', '.join(help_list))


        # list all the admins with a () around their name to avoid pinging them
        elif cmd_whole in ['admin', 'admins', 'adminlist', 'adminslist']:
            admin_list = []
            for admin in admins:
                admin_list.append('(' + admin + ')')
            self.message('List of Admins: ' + ', '.join(admin_list))


        # list all bttv emotes
        elif cmd_whole in ['bttvemotes', 'emotes', 'emoteslist']:
            self.message('EZ  Clap  HYPERCLAP  SPANK  SPANKED  FeelsGoldMan')


        # add new commands
        elif cmd in ['newcommand', 'addcommand', 'createcommand'] and user in admins:
            if len(arguments) < 4 or arguments[2].lower() not in ['admin', 'common']:
                self.syntax(cmd)
            else:
                # remove the ! at the beginning of the new command name if present
                new_name = word_fixer(arguments[1])
                common_commands_list = get_commands_list()
                if new_name in common_commands_list:
                    self.message(new_name + ' command already exists')

                # add the new command
                else: 
                    common_commands_file_write = open(commands_file_string, "a")
                    new_permission = word_fixer(arguments[2])
                    common_commands_file_write.write('\n' + new_name + '::' + new_permission + '::')
                    for a in range(3, len(arguments)):
                        common_commands_file_write.write(arguments[a] + ' ')
                    print(user + ' created ' + new_name + '  command.')
                    self.message('Successfully created ' + new_name + ' command')
                    common_commands_file_write.close()


        #remove commands
        elif cmd in ['deletecommand', 'removecommand'] and user in admins:
            # make sure the command has the correct syntax
            if len(arguments) != 2:
                self.syntax(cmd)
            else: 
                # remove ! at the beginning of the command name if present
                name = word_fixer(arguments[1])

                # store commands.json in replace
                # edit replace
                # re-write commands.json with edited replace
                replace = []
                common_commands_list = get_commands_list()
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
                        print(user + ' deleted ' + name + ' command.')
                        self.message('Successfully deleted ' + name + ' command')
                else:
                    self.message(name + ' command does not exist')




        ########## POINTS RELATED COMMANDS ##############
        # check the points of users
        elif cmd == 'points':
            if len(arguments) == 1:
                if self.add_user(user):
                    self.message(user + ' has ' + format(points.get_points(user), ',d') + ' points')
            elif len(arguments) == 2:
                username = word_fixer(arguments[1])

                if username in ['top', 'richest']:
                    top = points.get_bot()
                    self.message(top[len(top)-1][0] + ' is the richest with ' + format(top[len(top)-1][1], ',d') + ' points! POGGERS')
                elif username in['bottom', 'bot', 'poorest']:
                    bot = points.get_bot()
                    self.message(bot[0][0] + ' is the poorest with ' + format(bot[0][1], ',d') + ' points. PressF')
                else:
                    if self.add_user(username):
                        self.message(username + ' has ' + format(points.get_points(username), ',d') + ' points')
            else:
                self.syntax(cmd)


        # add points to users
        elif cmd == 'addpoints' and user in admins:
            if len(arguments) != 3:
                self.syntax(cmd)
            else:
                username = word_fixer(arguments[1])

                try:
                    add = int(arguments[2])
                    if username in ['everyone', 'everybody']:
                        points.add_points(username, add)
                        self.message('everyone has been given ' + format(add, ',d') + ' points! Kreygasm')                    
                    elif self.add_user(username):
                        points.add_points(username, add)
                        self.message(self.user_balance(username))
                except ValueError:
                    self.message(arguments[2] + ' is not a number')                       


        # subtract points from users
        elif cmd in ['subpoints', 'removepoints', 'deletepoints'] and user in admins:
            if len(arguments) != 3:
                self.syntax(cmd)
            else:
                username = word_fixer(arguments[1])

                if arguments[2].lower() == 'all':
                        arguments[2] = points.get_points(username)

                try:
                    sub = int(arguments[2]) * -1
                    if username in ['everyone', 'everybody']:
                        points.add_points(username, sub)
                        self.message('everyone has lost ' + format(sub * -1, ',d') + ' points. FeelsBadMan')            
                    elif self.add_user(username):
                        points.add_points(username, sub)
                        self.message(self.user_balance(username))
                except ValueError:
                    self.message(arguments[2] + ' is not a number')


        elif cmd == 'setpoints' and user in admins:
            if len(arguments) != 3:
                self.syntax(cmd)
            else:
                username = word_fixer(arguments[1])

                try:
                    value = int(arguments[2])
                    if username in ['everyone', 'everybody']:
                        points.set_points(username, value)
                        self.message('everyone has had their points reset to ' + format(value, ',d') + ' points.')
                    elif self.add_user(username):
                        points.set_points(username, value)
                        self.message(self.user_balance(username))
                except ValueError:
                    self.message(arguments[2] + ' is not a number')



        elif cmd in ['multpoints', 'multiplypoints']:
            if len(arguments) != 3:
                self.syntax(cmd)
            else:
                username = word_fixer(arguments[1])

                if username in ['everyone', 'everybody']:
                    if self.illegal_value_check(arguments[2]):
                        multiplier = int(arguments[2])
                        points.mult_points(username, multiplier)
                        self.message('everyone has had their points multiplied by ' + str(multiplier) + '! Kreygasm')
                elif self.user_exists_check(username):
                    if self.illegal_value_check(arguments[2]):
                        multiplier = int(arguments[2])
                        points.mult_points(username, multiplier)
                        self.message(self.user_balance(username))



        elif cmd in ['divpoints', 'dividepoints']:
            if len(arguments) != 3:
                self.syntax(cmd)
            else:
                username = word_fixer(arguments[1])

                if username in ['everyone', 'everybody']:
                    if self.illegal_value_check(arguments[2]):
                        multiplier = int(arguments[2])
                        points.div_points(username, multiplier)
                        self.message('everyone has had their points divided by ' + str(multiplier) + '. FeelsBadMan')
                elif self.user_exists_check(username):
                    if self.illegal_value_check(arguments[2]):
                        multiplier = int(arguments[2])
                        points.div_points(username, multiplier)
                        self.message(self.user_balance(username))






        # allow users to give or donate their points
        elif cmd in ['givepoints', 'donatepoints']:
            if len(arguments) != 3:
                self.syntax(cmd)
            else:
                donator = word_fixer(user)
                recipient = word_fixer(arguments[1])

                if arguments[2].lower() == 'all':
                    arguments[2] = points.get_points(donator)

                if self.points_check(donator, arguments[2]):
                    if (self.user_exists_check(recipient)):
                        value = int(arguments[2])
                        points.donate_points(donator, recipient, value)
                        self.message(self.user_balance(donator) + ' && ' + self.user_balance(recipient))



        # allow players to gamble their points
        # generate a number from 0 to 100
        # if <50, player loses
        # if >50, player wins
        # if =50, no change
        # if =100, player wins double. jackpot!
        elif cmd == 'gamble':
            if len(arguments) != 2:
                self.syntax(cmd)
            else:
                if arguments[1].lower() == 'all':
                    arguments[1] = points.get_points(user)
                if self.points_check(user, arguments[1]):
                    value = int(arguments[1])
                    result = rng(0, 100)
                    if result < 50:
                        points.add_points(user, value * -1)
                        self.message(user + ' rolled a ' + str(result) + ' and has lost ' + format(value, ',d') +
                            ' points! you now have ' + format(points.get_points(user), ',d') + ' points.')
                    elif result > 50 and result < 100:
                        points.add_points(user, value)
                        self.message(user + ' rolled a ' + str(result) + ' and has won ' + format(value, ',d') +
                            ' points! you now have ' + format(points.get_points(user), ',d') + ' points.')
                    elif result == 100:
                        points.add_points(user, value * 2)
                        self.message(user + ' rolled a ' + str(result) + '! JACKPOT! you have won ' + format(value * 2, ',d') + 
                            ' points! you now have ' + format(points.get_points(user), ',d') + ' points.')
                    elif result == 50:
                        self.message(user + ' rolled a ' + str(result) + ' and has tied! you have not won or lost any points.')


        # guarantees a 100 every time
        elif cmd == 'admingamble' and user in admins:
            if len(arguments) != 2:
                self.syntax(cmd)
            else:
                if arguments[1].lower() == 'all':
                    arguments[1] = points.get_points(user)
                if self.points_check(user, arguments[1]):
                    value = int(arguments[1])
                    result = 100
                    points.add_points(user, value * 2)
                    self.message(user + ' rolled a ' + str(result) + '! JACKPOT! you have won ' + format(value * 2, ',d') + 
                        ' points! you now have ' + format(points.get_points(user), ',d') + ' points.')



        # bidding for mystery points box
        elif cmd == 'bid':
            if len(arguments) != 2:
                self.syntax(cmd)
            elif not mystery_box.is_alive():
                self.message('A mystery points box hasn\'t spawned yet')
            else:
                if arguments[1].lower() == 'all':
                    arguments[1] = points.get_points(user)
                
                if self.points_check(user, arguments[1]):
                    value = int(arguments[1])
                    if value > mystery_box.get_top_bid():
                        mystery_box.bid(user, value)
                        self.message(mystery_box.get_top_bidder() + ' now has the highest bid with ' + format(mystery_box.get_top_bid(), ',d') + ' points!')
                    else:
                        self.message(user + ' your bid is not high enough')


        elif cmd in ['beatbid', 'beattopbid', 'beathighestbid']:
            if len(arguments) != 2:
                self.syntax(cmd)
            elif not mystery_box.is_alive():
                self.message('A mystery points box hasn\'t spawned yet')
            else:
                if self.points_check(user, arguments[1]):
                    value = int(arguments[1]) + mystery_box.get_top_bid()
                    if self.funds_check(value):
                        mystery_box.bid(user, value)
                        self.message(mystery_box.get_top_bidder() + ' now has the highest bid with ' + format(mystery_box.get_top_bid(), ',d') + ' points!')


        elif cmd_whole in ['topbid', 'highestbid']:
            if not mystery_box.is_alive():
                self.message('A mystery points box hasn\'t spawned yet')
            else: 
                self.message('The top bid is ' + format(mystery_box.get_top_bid(), ',d') + ' points by ' + mystery_box.get_top_bidder())









        elif cmd_whole in ['lottery', 'lotto', 'checklotto', 'checklottery']:
            self.message('The lottery is at ' + format(lottery.get_value(), ',d') + ' points! Buy a ticket with !buytickets <# of tickets> for 5 points each!')


        elif cmd in ['buytickets', 'buyticket', 'buytix']:
            if len(arguments) != 2:
                self.syntax(cmd)
            else:
                if self.illegal_value_check(arguments[1]):
                    qty = int(arguments[1])
                    cost = qty * 5
                    if self.points_check(user, cost):
                        if qty > lottery.get_remaining_tickets():
                            self.message('There aren\'t enough tickets. There are only ' + format(lottery.get_remaining_tickets(), ',d') + ' tickets left. WutFace')
                        else:
                            lottery.buy_ticket(user, qty)
                            self.message(user + ' now has ' + format(lottery.get_tickets(user), ',d') + ' lottery tickets.')


        elif cmd in ['tickets', 'ticket', 'tix']:
            if len(arguments) == 1:
                username = user
            elif len(arguments) == 2:
                username = word_fixer(arguments[1])
            else:
                syntax(cmd)

            if len(arguments) in [1, 2]:
                if lottery.user_exists_check(username):
                    self.message(username + ' has ' + format(lottery.get_tickets(username), ',d') + ' lottery tickets.')
                else:
                    self.message(username + ' has 0 lottery tickets.')









        # allow admins to spawn events
        elif cmd in ['event', 'spawnevent', 'spawn'] and user in admins:
            if len(arguments) != 2:
                self.syntax(cmd)
            else:
                event_name = arguments[1]
                if event_name.lower() in ['box', 'mysterybox', 'mysterypointsbox']:
                    event_thread = threading.Thread(target=self.mystery_box_event)
                    event_thread.daemon = True
                    event_thread.start()
                elif event_name.lower() in ['lottery', 'lotto']:
                    event_thread = threading.Thread(target=self.lottery_event)
                    event_thread.daemon = True
                    event_thread.start()












        ################# BASIC TEXT COMMANDS ######################
        else:
            common_commands_file = open('commands.json', "r")
            common_commands_list_full = [line.strip() for line in common_commands_file]
            common_commands_file.close()

            for common_commands in common_commands_list_full:
                parsed_command = common_commands.split('::')
                command_name = parsed_command[0]
                permission = parsed_command[1]
                output = parsed_command[2]

                if cmd_whole == command_name:
                    # admin commands
                    if permission == 'admin':
                        if user in admins:
                            self.message(output)
                        else:
                            self.message('I\'m afraid I can\'t let you do that, ' + user)
                    # common commands
                    elif permission == 'common':
                        self.message(output)




def update_points():
    while True:
        points.update_points(points.get_viewers())
        sleep(15)


def rng(min_value: [int], max_value: [int]) -> [int]:
    random.seed(None)
    return random.randint(min_value, max_value)



def word_fixer(input: [str]) -> [str]:
    if input[0] in ['!', '@']:
        return input[1:].lower()
    else:
        return input.lower()


def get_commands_list() -> [list]:
    commands_file_string = 'commands.json'

    # common_commands_file is the file we'll store commands anyone can use and their functionalities
    # syntax for the file is [command name]::[permission]::[output]
    common_commands_file = open(commands_file_string, "r")

    #reads each line without the \n
    common_commands_list_full = [line.strip() for line in common_commands_file]
    common_commands_list = []
    for com in common_commands_list_full:
        common_commands_list.append(com[:com.find('::')])

    common_commands_file.close()

    return common_commands_list



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

    points_thread = threading.Thread(target=update_points)
    points_thread.daemon = True
    points_thread.start()

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()