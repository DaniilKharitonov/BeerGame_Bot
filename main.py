import telebot
import time
from telebot import types
from env import BeerGame
import os


class BeerGameBot:

    def __init__(self):
        self.n_users = 2 # Number of the game users, constant for each game.
        self.players = {1: [None]*self.n_users} # Dictionary of the {room: players}. The order conform player role
        self.status = {1: 0} # Dictionary of the {room: game status}
        """ Game statuses are:
        0 - Game did, not began
        0 < status < (n_users + 1)- There is 'status' registered users
        (n_users + 1) - Game has began, and first moves are made """
        self.step = {1: [-1]*self.n_users} # Dictionary of the {room: current game step for each user}
        self.joiners = {0: 0} # Dictionary of the {player: potential room to follow}
        self.env = {1: None} # Dictionary of the {room: BeerGameEnv}
        self.n_terns_per_game = 30 # Number of game rounds
        self.admin = '359144162'
        API_TOKEN = '986860158:AAGMZWfJlQEHmgEZeYaeOfpk0nxM0QoCjrE'
        self.bot = telebot.TeleBot(API_TOKEN)
        self.bot.message_handler(func=lambda message: True)(self.message_respond)
        self.bot.callback_query_handler(func=lambda call: True)(self.call_respond)

    # Responds and functions for messages
    def message_respond(self, message):
        if message:
            if message.text == '/start':
                self.start_message(message)
            elif message.text == '/help':
                self.help(message)
            elif message.text == '/start_new_game':
                self.start_new_game(message)
            elif message.text == '/join_created_game':
                self.join_created_game(message)
            elif message.text == '/restart':
                self.restart_the_game(message)
            elif message.text == '/status':
                self.player_status(message.chat.id)
            else:
                # If player is in the game he inserting his step. If player is joining the game he inserting the room.
                if self.find_room(message) or (message.chat.id in self.joiners):
                    self.check(message)
                else:
                    self.bot.send_message(message.chat.id, message.text)

    # Responds and functions for calls
    def call_respond(self, call):
        if call.message:
            if call.data == '/start_new_game':
                self.start_new_game(call.message)
            elif call.data == '/help':
                self.help(call.message)
            elif call.data == '/read_rules':
                self.read_rules(call.message)
            elif call.data == '/restart_the_game':
                if call.message.chat.id in self.joiners:
                    if self.joiners[call.message.chat.id] != 0:
                        self.bot.send_message(call.message.chat.id, 'Press /start')
                        self.restart_the_game(self.joiners[call.message.chat.id])
                    elif call.message.chat.id in self.players:
                        self.bot.send_message(call.message.chat.id, 'Press /start')
                        self.restart_the_game(self.find_room(call.message.chat.id))
            elif call.data == '/continue_the_game':
                self.restart_the_game(call.message)
            elif call.data == '/join_created_game':
                self.join_created_game(call.message)
            elif call.data in ['/retailer', '/distributor', '/wholesaler', '/giant_wholesaler', '/manufacturer']:
                if call.message.chat.id in self.joiners:
                    self.set_the_player(call)
            else:
                print(call.message)

    # First message you get when you came to Bot /Completed
    def start_message(self, message):
        room = self.find_room(message)
        if not room:
            self.bot.send_message(chat_id=message.chat.id,
                                  text='Hi, I am BeerGame_Bot. With my help you can play popular Beer Game.\n'
                                       'Join me!\n')
            bt_start_actions = ['Help', 'Read rules', 'Start NEW Game', 'Join Created Game']
            self.make_inline_buttons(message, bt_start_actions, 'What do you want me to do?', 1)
        else:
            self.bot.send_message(chat_id=message.chat.id,
                                  text='Hi again, I am BeerGame_Bot.\n'
                                       'As i can see you current participant of the game #{}\n'.format(room))
            bt_possible_actions = ['Continue the Game', 'Restart the Game']
            self.make_inline_buttons(message, bt_possible_actions, 'What do you want me to do?', 1)
        print(message.chat.id, '\n')

    # Creating the room for the new game
    def start_new_game(self, message):
        room = self.find_room(message)
        print(room)
        print(message.chat.id in self.joiners)
        if room or message.chat.id in self.joiners:
            if room:
                self.restart_the_game(room)
            elif message.chat.id in self.joiners and self.joiners[message.chat.id] in self.players:
                self.restart_the_game(self.joiners[message.chat.id])
            self.bot.send_message(message.chat.id, "Your previous game was finished")
        new_room = list(self.players.keys())[-1] + 1
        self.players.update({new_room: [None]*self.n_users})
        self.status.update({new_room: 0})
        self.step.update({new_room: [-1] * self.n_users})
        self.env.update({new_room: BeerGame(n_agents=self.n_users, env_type='classical',
                                        n_turns_per_game=self.n_terns_per_game)})
        self.joiners.update({message.chat.id: new_room})
        self.bot.send_message(message.chat.id, "New Game was created. Its' number: {}\n"
                                               "To get your friends at this game ask them\n"
                                               "to 'Join Created Game' in start menu with this number".format(new_room))
        self.choose_players(message)
        self.print()

    # Defines all user messages that could influence the bot /Completed
    def help(self, message):
        self.bot.send_message(message.chat.id, 'Try next functions to solve problem you have:\n\n'
                                               '/start - starts the conversation with the bot from the beginning if '
                                               'the Beer Game has not began yet. Your access will be denied if it has\n'
                                               '/restart - restarts the whole game, if you current participant\n'
                                               '/continue_the_game - starts the game from the place you leaved\n'
                                               '/status - shows your current status in the game\n'
                                               '/help - shows short summary of all functions\n'
                                               '\n If you still have questions contact @har_anad \n')

    # For the player that join someones game
    def join_created_game(self, message):
        room = self.find_room(message)
        if (not message.chat.id in self.joiners) and (not room):
            self.joiners.update({message.chat.id: 0})
            self.bot.send_message(message.chat.id, 'Send me message with the number of the game you are want to join')
        elif room:
            self.bot.send_message(message.chat.id, 'You are also playing the game #{}'.format(room))
            bt_possible_actions = ['Continue the Game', 'Restart the Game']
            self.make_inline_buttons(message, bt_possible_actions, 'What do you want me to do?', 1)
        else:
            self.bot.send_message(message.chat.id, 'You are also joining the game #{}'.
                                  format(self.joiners[message.chat.id]))
            bt_possible_actions = ['Join Created Game', 'Restart the Game']
            self.make_inline_buttons(message, bt_possible_actions, 'What do you want me to do?', 1)
        self.print()

    # Choosing the character in interface
    def choose_players(self, message):
        room = self.find_room(message)
        bt_player_role = ['Retailer', 'Distributor', 'Wholesaler', 'Giant Wholesaler']
        bt_player_role = bt_player_role[:self.n_users-1]
        bt_player_role.append('Manufacturer')

        if not room:
            room = self.joiners[message.chat.id]
            if self.status[room] < self.n_users:
                self.make_inline_buttons(message, bt_player_role[:self.n_users],
                                         "Choose, who are you in that retail chain?", 2)
            elif message.chat.id != self.admin:
                self.bot.send_message(message.chat.id, "Sorry the Beer Game has began, try it later\n"
                                                       "To contact admin, press /help")
            else:
                self.bot.send_message(message.chat.id, "The Beer Game has began. Do you want to restart it?\n")
                bt_restart = ['Restart the game', 'Continue the game']
                self.make_inline_buttons(message, bt_restart, "What do you want me to do?", 1)
        else:
            self.continue_the_game(message)

    # Setting the player in program
    def set_the_player(self, call):
        room = self.find_room(call.message)
        cl_player_role = ['/retailer', '/distributor', '/wholesaler', '/giant_wholesaler']
        cl_player_role = cl_player_role[:(self.n_users - 1)]
        cl_player_role.append('/manufacturer')

        if not room:
            room = self.joiners[call.message.chat.id]
            if self.status[room] < self.n_users:
                sl_number = cl_player_role.index(call.data)  # selected number

                if self.players[room][sl_number] == None:
                    self.players[room][sl_number] = call.message.chat.id
                    self.status[room] += 1
                    del self.joiners[call.message.chat.id]
                    self.continue_the_game(call.message)
                else:
                    self.bot.send_message(call.message.chat.id, 'Someone selected this part of the chain, try another')

        elif self.status[room] < self.n_users:
            self.bot.send_message(call.message.chat.id,
                                  "You've done everything you needed to do. Just wait for your turtle friend")
        else:
            self.continue_the_game(call.message)
        print(self.players[room])

    def continue_the_game(self, message):
        room = self.find_room(message)
        if self.status[room] < self.n_users and room:
            self.bot.send_message(message.chat.id,
                                  "You have selected the role. Now just wait for your friends\n"
                                  "If it takes too much time, just press restart in /help")
            print("Room {}. Current status {}".format(room, self.status[room]))
        elif self.status[room] == self.n_users:
            self.status[room] += 1
            self.env[room].reset()

            for tmp in self.players[room]:
                self.bot.send_message(tmp, 'Ready to start?')
            for dialog in self.players[room]:
                self.bot.send_message(dialog, 'Beer Game is beginning right now!\n')
                self.bot.send_message(dialog, 'Current situation is following...')
            self.game_status(room)

            for dialog in self.players[room]:
                self.bot.send_message(dialog, 'Now you are able to order some beer. Just send me the INTEGER number')
        else:
            self.game_step(message)

    # Sending message about current status
    def game_status(self, room):
        for dialog in self.players[room]:
            self.player_status(dialog)

    # Message to concreet player
    def player_status(self, dialog):
        room = self.find_room(dialog)
        index = self.players[room].index(dialog)
        status = self.env[room]._get_observations()
        self.bot.send_message(dialog, "Previously Placed Orders: {}\n"
                                      "Incoming Order:           {}\n\n"
                                      "Current Stock:            {}\n"
                                      "Previous Shipments:        ↓\n"
                                      "                          {}\n"
                                      "                           ↓\n"
                                      "                          {}\n".format(status[index]['orders'],
                                                                              status[index]['next_incoming_order'],
                                                                              status[index]['current_stock'],
                                                                              status[index]['shipments'][0],
                                                                              status[index]['shipments'][1]))

    # Game step
    def game_step(self, message):
        room = self.find_room(message.chat.id)
        pl_index = self.players[room].index(message.chat.id)
        if self.step[room][pl_index] == -1:
            self.step[room][pl_index] = int(message.text)
        else:
            self.bot.send_message(message.chat.id, "You ordered {} new beer.\n"
                                                   "Wait for your friends\n".format(self.step[room][pl_index]))
        print(self.step[room])
        if -1 not in self.step[room]:
            self.env[room].step(self.step)
            self.game_status(room)

            self.status[room] += 1
            self.step[room] = [-1] * self.n_users
            print(self.status[room], '\n', self.step[room])

            if self.env[room].done:
                self.finish(room)

    def finish(self, room):
        sum = 0
        for dialog in self.players[room]:
            index = self.players[room].index(dialog)
            status = self.env[room]._get_observations()
            self.bot.send_message(dialog, "Uraaaaaaaa!")
            self.bot.send_message(dialog, "Game is over, your score: {}".format(status[index]['cum_cost']))

            sum += status[index]['cum_cost']
        for dialog in self.players[room]:
            self.bot.send_message(dialog, "Total score of your team: {}".format(sum))
        self.restart_the_game(room)

    # Checks if player in the game or trying to join
    def check(self, message):
        room = self.find_room(message)
        # Game has began, sending number is the step
        if room and (self.status[room] > self.n_users):
            try:
                tmp_value = int(message.text)
                if tmp_value >= 0:
                    self.continue_the_game(message)
                else:
                    self.bot.send_message(message.chat.id, "Please insert not negative INTEGER values")
            except (TypeError, ValueError):
                self.bot.send_message(message.chat.id, "Please insert only INTEGER values")
        # Player trying to join the game
        elif message.chat.id in self.joiners:
            try:
                tmp_value = int(message.text)
                print([tmp_value]*11)
                if tmp_value == 1:
                    tmp_value = 0
                if tmp_value in self.players:
                    if self.status[tmp_value] < self.n_users:
                        self.joiners[message.chat.id] = tmp_value
                        self.choose_players(message)
                    else:
                        self.bot.send_message(message.chat.id, "Sorry the Beer Game # {} has began.\n"
                                                               "You can start your own game".format(tmp_value))
                else:
                    self.bot.send_message(message.chat.id, "There is no such game, check if you entered "
                                                           "the right number and try it again. \n"
                                                           "You can start your own game")
            except (TypeError, ValueError):
                self.bot.send_message(message.chat.id, "Please insert only INTEGER values")
        else:
            self.bot.send_message(message.chat.id, "Something went wrong. Please go to /help")

    # Restart the game by call
    def restart_the_game(self, room):
        del self.players[room]
        del self.status[room]
        del self.step[room]
        del self.env[room]
        deletion = []
        for player in self.joiners:
            if self.joiners[player] == room:
                deletion.append(player)
        for player in deletion:
            del self.joiners[player]
        self.print()

    def print(self):
        print('Room: {}\nJoiners: {}\nStatus: {}\nStep: {}'.
              format(self.players, self.joiners, self.status, self.step))

    # Restart the game with message
    def restart_the_game_message(self, message):
        room = self.find_room(message)
        if room:
            del self.players[room]
            del self.status[room]
            del self.step[room]
            del self.env[room]
            self.print()

    # Makes button that shows Link where you can find rules
    def read_rules(self, message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="Show me the rules", url="https://google.com"))
        self.bot.send_message(message.chat.id, "You can push button bellow and find rules.", reply_markup=markup)

    # Makes reply button for responds
    def make_reply_buttons(self, message, buttons, message_text, width):
        if buttons and width is not None:
            markup = types.ReplyKeyboardMarkup(row_width=width)
            for i in range(buttons.__len__()):
                markup.add(buttons[i])
            self.bot.send_message(chat_id=message.chat.id, text=message_text, reply_markup=markup)
            return
        else:
            return

    # Makes inline button for responds
    def make_inline_buttons(self, message, buttons, message_text, width):
        if buttons and width is not None:
            calls = ['/' + tmp.lower() for tmp in buttons]
            calls = ['_'.join(tmp.split(' ')) for tmp in calls]

            markup = types.InlineKeyboardMarkup(row_width = width)
            for i in range(buttons.__len__()):
                markup.add(types.InlineKeyboardButton(text=buttons[i], callback_data=calls[i]))
            self.bot.send_message(chat_id=message.chat.id, text=message_text, reply_markup=markup)
            return
        else:
            return

    # Finds room player if player had joined thr game
    def find_room(self, message):
        room = 0
        for i in self.players:
            if message.chat.id in self.players[i]:
                room = i
        return room

New_Session = BeerGameBot()
New_Session.bot.polling()
