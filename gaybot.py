import sys
import irc.bot
import requests
import threading
import json
from time import sleep

# my own libraries
import points
import commands
import events.bot_events as bot_events
from utilities import rng



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

# make variable names consistent: events should have 'players' not 'users'
# find a better way to display commands when user types !help
# users can guarantee a win on lottery by buying max tickets and they'll always make a profit, find some way to balance this


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

        self.points = points.Points()
        self.events = bot_events.BotEvents(self.connection, self.channel, self.points)


    def message(self, output: str):
        self.connection.privmsg(self.channel, output)


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
        args = cmd_raw.lower().split(' ')
        user = e.source[:e.source.find('!')]

        cmd = commands.Commands(user, args, self.points, self.events)
        self.message(cmd.execute())


    def update_points(self):
        while True:
            self.points.update_points()
            self.points.save()
            sleep(15)

   
    def event_timer(self):
        time_min = 15 # in minutes
        time_max = 30 # in minutes
        while True:
            sleep(rng(time_min * 60, time_max * 60)) # conver from min to seconds
            event_list = ['box', 'lotto']
            event_number = rng(0, len(event_list) - 1)
            self.events.start_event(event_list[event_number])









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

    try:
        bot = TwitchBot(username, client_id, token, channel)
        bot.start()
    except KeyboardInterrupt:
        bot.message('bot has committed honorable sudoku')
        bot.points.save()
        bot.events.lottery.save()
    except:
        bot.message('someone murdered me.')
        bot.points.save()
        bot.events.lottery.save()
        raise

if __name__ == "__main__":
    main()