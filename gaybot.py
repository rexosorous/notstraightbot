import irc.bot
import requests
import threading
import random
import json
import queue
import os
from time import sleep

# my own libraries
import points
import mystery_box
import lottery
import bomb_squad
import utilities as util
import redeem


############ TO DO #################

# learn about classes so i don't have to keep loading json files

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
# ideas for more sound effects:
#	jump scare


bomb_q = queue.Queue()


class TwitchBot(irc.bot.SingleServerIRCBot):
	def __init__(self, username, client_id, token, channel):
		self.blacklist = util.load_file('blacklist.json')

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


	def message(self, output: str):
		self.connection.privmsg(self.channel, output)


	def update_points(self):
		while True:
			points.update_points([x for x in get_viewers() if x not in self.blacklist])
			sleep(15)


   
	def event_timer(self):
		time_min = 15 # in minutes
		time_max = 30 # in minutes
		while True:
			sleep(rng(time_min * 60, time_max * 60)) # sleep(x) sleeps for x seconds
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

			if mystery_box.get_top_bidder() == '':
				self.message('the box disappears, saddened that no one bid on it BibleThump')
				print ('[box] despawned with no winners')
				mystery_box.cleanup()
			else:
				winner = mystery_box.get_top_bidder()
				bid = mystery_box.get_top_bid()
				box_points = mystery_box.get_box_points()

				points.change_points(winner, box_points, '+')

				self.message(f'{winner} has won the mystery box with a bid of {bid:,} points! Congratulations!')
				self.message(f'The box contained {mystery_box.get_box_points():,} points! {winner} now has {points.get_points(winner):,} points.')
				print (f'[box] {winner} has won the box')

				mystery_box.cleanup()


	def lottery_event(self):
		print ('[lottery] is being drawn')
		self.message('The winning lottery ticket will be drawn in 1 minute! Buy your tickets for 5 points with !buytickets <qty>.')
		sleep(60)
		winner = lottery.draw()
		self.message('The winning lottery ticket has been drawn and...')
		sleep(3)
		if winner:
			self.message(f'{winner} won the lottery! You won {lottery.get_value():,} points, giving you {points.get_points(winner):,} points total! EZ Clap')
			lottery.cleanup()
			print (f'[lottery] {winner} won the lottery')
		else:
			self.message('Nobody won the lottery PepeREE')
			print ('[lottery] no winners')


	def bomb_event(self):
		if not bomb_squad.is_alive():
			print ('[bomb] starting')
			bomb_squad.start()
			self.message('Calling all bomb squad technicians, there\'s a bomb at the orphanage! You\'ll have one minute to join this event with !bomb join')
			sleep(60)
			if not bomb_squad.new_round():
				print('[bomb] not enough players to start')
				self.message('There aren\'t enough players to start the event.')
				bomb_squad.cleanup()


	def bomb_timer(self, active_player: str):
		bomb_thread = threading.Thread(target=self.bomb_timeout, args=[active_player])
		bomb_thread.daemon = True
		bomb_thread.start()
		# i can use queue module instead of writing to json files https://pymotw.com/2/Queue/
		# so instead of having to write to json files to make sure all my threads are using the same data, i can use queues


	def bomb_timeout(self, active_player: str):
		# if after 15 seconds a player hasn't made a choice, eliminate them from the game
		sleep(15)
		try:
			temp = bomb_q.get()
		except Queue.Empty:
			self.message(f'{active_player}, you waited too long and the bomb blew up on you!')
			bomb_squad.elim_player(active_player)

 

	# checks if a user exists in our db
	def user_exists_check(self, user: str) -> bool:
		if points.user_exists_check(user):
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
		if int(value) > points.get_points(user):
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
		rstring = f'{user} now has {points.get_points(user):,} points'
		return rstring


	def add_user(self, user: str) -> bool:
		if user in self.blacklist:
			self.message(f'{user} is banned from this bot.')
			return
		if not points.user_exists_check(user):
			chat = get_viewers()
			if user in chat:
				points.add_user(user)
				return True
			else:
				self.message(f'{user} is not in chat.')
				return False
		else:
			return True


	def syntax(self, cmd_whole: str):
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

		points_thread = threading.Thread(target=self.update_points)
		points_thread.daemon = True
		points_thread.start()

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
		admins = {'gay_zach', 'hwangbroxd'}
		cmd_whole = cmd_whole.lower()
		arguments = cmd_whole.split(' ')
		cmd = arguments[0]
		user = e.source[:e.source.find('!')] # the user who sent the message


		############ SPECIAL COMMANDS ###################
		# list all the commands
		if user in self.blacklist:
			self.message(f'{user} is banned from this bot')
			return

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
					print(f'{user} created {new_name} command.')
					self.message(f'Successfully created {new_name} command')
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
						print(f'{user} deleted {name} command.')
						self.message(f'Successfully deleted {name} command')
				else:
					self.message(f'{name} command does not exist')


		elif cmd == 'ban' and user in admins:
			if len(arguments) != 2:
				self.syntax(cmd)
			else:
				target = word_fixer(arguments[1])
				if target not in admins:
					if target in self.blacklist:
						self.message('that user is already banned')
					else:
						self.blacklist.append(target)
						points.remove_user(target)
						util.write_file('blacklist.json', self.blacklist)
						self.message(f'{target} has been banned from this bot')

		elif cmd == 'unban' and user in admins:
			if len(arguments) != 2:
				self.sytnax(cmd)
			else:
				target = word_fixer(arguments[1])
				if target not in self.blacklist:
					self.message('that user was not already banned')
				else:
					self.blacklist.remove(target)
					util.write_file('blacklist.json', self.blacklist)
					self.message(f'{target} has been unbanned from this bot')




		########## POINTS RELATED COMMANDS ##############
		# check the points of users
		elif cmd == 'points':
			if len(arguments) == 1:
				if self.add_user(user):
					self.message(f'{user} has {points.get_points(user):,} points')
			elif len(arguments) == 2:
				username = word_fixer(arguments[1])

				if username in ['top', 'richest']:
					top = points.get_bot()
					self.message(f'{top[len(top)-1][0]} is the richest with {top[len(top)-1][1]:,} points! POGGERS')
				elif username in['bottom', 'bot', 'poorest']:
					bot = points.get_bot()
					self.message(f'{bot[0][0]} is the poorest with {bot[0][1]:,} points. PressF')
				else:
					if self.add_user(username):
						self.message(f'{username} has {points.get_points(username):,} points')
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
					if username in points.everyone:
						points.change_points(username, add, '+')
						self.message(f'everyone has been given {add:,} points! Kreygasm')                    
					elif self.add_user(username):
						points.change_points(username, add, '+')
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
					sub = int(arguments[2])
					if username in points.everyone:
						points.change_points(username, sub, '-')
						self.message(f'everyone has lost {sub * -1:,} points. FeelsBadMan')            
					elif self.add_user(username):
						points.change_points(username, sub, '-')
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
					if username in points.everyone:
						points.set_points(username, value)
						self.message(f'everyone has had their points reset to {value:,} points.')
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

				if username in points.everyone:
					if self.illegal_value_check(arguments[2]):
						multiplier = int(arguments[2])
						points.change_points(username, multiplier, '*')
						self.message(f'everyone has had their points multiplied by {multiplier}! Kreygasm')
				elif self.user_exists_check(username):
					if self.illegal_value_check(arguments[2]):
						multiplier = int(arguments[2])
						points.change_points(username, multiplier, '*')
						self.message(self.user_balance(username))



		elif cmd in ['divpoints', 'dividepoints']:
			if len(arguments) != 3:
				self.syntax(cmd)
			else:
				username = word_fixer(arguments[1])

				if username in points.everyone:
					if self.illegal_value_check(arguments[2]):
						multiplier = int(arguments[2])
						points.change_points(username, multiplier, '/')
						self.message(f'everyone has had their points divided by {multiplier}. FeelsBadMan')
				elif self.user_exists_check(username):
					if self.illegal_value_check(arguments[2]):
						multiplier = int(arguments[2])
						points.change_points(username, multiplier, '/')
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
						points.change_points(user, value, '-')
						self.message(f'{user} rolled a {result} and has lost {value:,} points! you now have {points.get_points(user):,} points.')
					elif result > 50 and result < 100:
						points.change_points(user, value, '+')
						self.message(f'{user} rolled a {result} and has won {value:,} points! you now have {points.get_points(user):,} points.')
					elif result == 100:
						points.change_points(user, value * 2, '+')
						self.message(f'{user} rolled a {result}! JACKPOT! you have won {value * 2:,} points! you now have {points.get_points(user):,} points.')
					elif result == 50:
						self.message(f'{user} rolled a {result} and has tied! you have not won or lost any points.')


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
					points.change_points(user, value * 2, '+')
					self.message(f'{user} rolled a {result}! JACKPOT! you have won {value * 2:,} points! you now have {points.get_points(user):,} points.')


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
						self.message(f'{mystery_box.get_top_bidder()} now has the highest bid with {mystery_box.get_top_bid():,} points!')
					else:
						self.message(f'{user} your bid is not high enough')


		elif cmd in ['beatbid', 'beattopbid', 'beathighestbid']:
			if len(arguments) != 2:
				self.syntax(cmd)
			elif not mystery_box.is_alive():
				self.message('A mystery points box hasn\'t spawned yet')
			else:
				if self.points_check(user, arguments[1]):
					value = int(arguments[1]) + mystery_box.get_top_bid()
					if self.funds_check(user, value):
						mystery_box.bid(user, value)
						self.message(f'{mystery_box.get_top_bidder()} now has the highest bid with {mystery_box.get_top_bid():,} points!')


		elif cmd_whole in ['topbid', 'highestbid']:
			if not mystery_box.is_alive():
				self.message('A mystery points box hasn\'t spawned yet')
			else: 
				self.message(f'The top bid is {mystery_box.get_top_bid():,} points by {mystery_box.get_top_bidder()}')









		elif cmd_whole in ['lottery', 'lotto', 'checklotto', 'checklottery']:
			self.message(f'The lottery is at {lottery.get_value():,} points! Buy a ticket with !buytickets <# of tickets> for 5 points each!')


		elif cmd in ['buytickets', 'buyticket', 'buytix']:
			if len(arguments) != 2:
				self.syntax(cmd)
			else:
				if self.illegal_value_check(arguments[1]):
					qty = int(arguments[1])
					cost = qty * 5
					if self.points_check(user, cost):
						if qty > lottery.get_remaining_tickets():
							self.message(f"There aren't enough tickets. There are only {lottery.get_remaining_tickets():,} tickets left. WutFace")
						else:
							lottery.buy_ticket(user, qty)
							self.message(f'{user} now has {lottery.get_tickets(user):,} lottery tickets.')


		elif cmd in ['tickets', 'ticket', 'tix']:
			if len(arguments) == 1:
				username = user
			elif len(arguments) == 2:
				username = word_fixer(arguments[1])
			else:
				syntax(cmd)

			if len(arguments) in [1, 2]:
				if lottery.user_exists_check(username):
					self.message(f'{username} has {lottery.get_tickets(username):,} lottery tickets.')
				else:
					self.message(f'{username} has 0 lottery tickets.')


		elif cmd_whole in ['bomb', 'bombsquad']:
			if bomb_squad.is_alive():
				if len(arguments) == 1:
					self.message(f'Remaining players: {bomb_squad.get_players()}')
				elif len(arguments) == 2:
					arg = word_fixer(arguments[1])
					if arg =='join':
						if not bomb_squad.in_progress():
							bomb_squad.join(user)
							self.message(f'{user} has joined the bomb squad event')
						else:
							self.message('The bomb squad event has already started.')

			else:
				self.message('The bomb squad event hasn\'t started yet.') 


		elif cmd in ['cut', 'cutwire']:
			if len(arguments) == 2:
				if user == bomb_squad.get_active_player():
					wire_num = word_fixer(arguments[2])
					if illegal_value_check(wire_num):
						wire_num = int(wire_num)
						if wire_num in bomb_squad.get_avail_wires():
							self.message(f'{user} cuts wire #{wire_num} and...')
							sleep(3)
							self.message(bomb_squad.choose_wire(user, wire_num))
						else:
							self.message('You can\'t cut that wire.')
				else:
					self.message(f'It\'s {bomb_squad.get_active_player()}\'s turn, not yours.')
			else:
				syntax(cmd)












			# else:
			# 		arg = word_fixer(arguments[1])
			# 		if arg == 'join':
			# 			if len(arguments) == 2:
			# 				if not bomb_squad.in_progress():
			# 					bomb_squad.join(user)
			# 				else:
			# 					self.message('The bomb squad event is already in progress')
			# 		elif arg in ['cut', 'select', 'cutwire', 'selectwire']:
			# 			if len(arguments) == 3:
			# 				if user == bomb_squad.get_active_player():
			# 					wire_num = word_fixer(arguments[2]) # we want to let users type !bomb cut #2
			# 					if illegal_value_check(wire_num):
			# 						wire_num = int(wire_num)
			# 						if wire_num in bomb_squad.get_avail_wires():
			# 							self.message(f'{user} cuts wire #{wire_num} and...')
			# 							sleep(3)
			# 							if bomb_squad.choose_wire(user, wire_num):
			# 								self.message(f'{user} lives! Clap')
			# 								self.message(f'{bomb_squad.get_active_player()}, you\'re up next. Cut one of these wires with !bomb cut: {bomb_squad.get_avail_wires()}')
			# 								bomb_timeout(bomb_squad.get_active_player())
			# 							else:
			# 								self.message(f'{user} blew up the bomb! cmonBruh')
			# 								if not new_round():
			# 									self.message(f'{bomb_squad.get_players()} is the last man standing and won ') # figure out how many points to pay out
			# 									bomb_squad.cleanup()
			# 								else:
			# 									self.message(f'There\'s another bomb! {bomb_squad.get_active_player()}, you\'re up next. Cut one of these wires with !bomb cut: {bomb_squad.get_avail_wires()}')
			# 									bomb_timeout(bomb_squad.get_active_player())
			# 						else:
			# 							self.message('That wire has already been cut.')
			# 				else:
			# 					self.message(f'{user}, it\'s not your turn.')


















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



















		########################### REDEEM POINTS #########################
		elif cmd in ['redeem', 'redeempoints']:
			rewards = ['dejavu', '90s', 'gas', 'spacejam', 'countryroads', 'fitnessgram', 'skeleton', 'victoryell']
			if len(arguments) != 2:
				self.message('Syntax for that command is: !redeem <reward>. Type \"!redeem help\" for more info')
			else:
				arg = arguments[1]
				if arg == 'help':
					rewards_list = ', '.join(rewards)
					self.message(f'rewards cost 1000 points each. here is a list of all the rewards: {rewards_list}')
				else:
					if self.funds_check(user, 1000):
						points.change_points(user, 1000, '-')
						redeem_thread = threading.Thread(target=redeem.play_sound, args=(arg,))
						redeem_thread.daemon = True
						redeem_thread.start()



















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
							self.message(f"I'm afraid I can't let you do that, {user}")
					# common commands
					elif permission == 'common':
						self.message(output)





def get_viewers() -> str:
	url = r'https://tmi.twitch.tv/group/user/gay_zach/chatters'
	names = requests.get(url).json()

	# avoid getting timed out
	sleep(0.5)

	# formatted string
	return names['chatters']['viewers'] + names['chatters']['moderators']


def rng(min_value: int, max_value: int) -> int:
	random.seed(None)
	return random.randint(min_value, max_value)



def word_fixer(input: str) -> str:
	if input[0] in ['!', '@', '#']:
		return input[1:].lower()
	else:
		return input.lower()


def get_commands_list() -> list:
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

	if os.path.exists('box_info.json'):
		os.remove('box_info.json')

	try:
		bot = TwitchBot(username, client_id, token, channel)
		bot.start()
	except KeyboardInterrupt:
		bot.message('bot has committed honorable sudoku')

if __name__ == "__main__":
	main()