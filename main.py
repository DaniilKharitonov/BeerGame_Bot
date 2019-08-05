import os
import telebot
import time
from telebot import types


class BeerGameBot:

    def __init__(self):

        self.n_users = 2
        self.players = [0]*self.n_users
        self.step = [-1]*self.n_users
        self.admin = 'USER_ID'

        API_TOKEN = 'TOKEN'
        self.bot = telebot.TeleBot(API_TOKEN)

        """
        Game statuses are:
        0 - Game did, not began
        0 < status < (n_users + 1)- There is 'status' registered users
        (n_users + 1) - Game has began, and first moves are made
        """
        self.status = 0
        self.bot.message_handler(func = lambda message: True)(self.message_respond)
        self.bot.callback_query_handler(func = lambda call: True)(self.call_respond)

    def message_respond(self, message):
        if message:
            if message.text == '/start':
                self.start_message(message)
            elif message.text == '/help':
                self.help(message)
            elif message.text == '/start_the_game':
                self.start_the_game(message)
            else:
                self.bot.send_message(message.chat.id, message.text)

    def help(self, message):
        self.bot.send_message(message.chat.id, 'Try next functions to solve problem you have:\n\n'
                                               '/start - starts the conversation with the bot from the beginning if '
                                               'the Beer Game has not began yet. If it has your access will be denied\n'
                                               '/restart - restarts the whole game, if you current participant\n'
                                               '/start_the_game - starts the game from the place you leaved\n'
                                               '/status - shows your current status in the game\n'
                                               '/help - shows short summary of all functions\n'
                                               '\n If you still have questions contact @har_anad \n')

    def call_respond(self, call):
        if call.message:
            if call.data == '/start_the_game':
                self.start_the_game(call.message)
            elif call.data == '/help':
                self.help(call.message)
            elif call.data == '/read_rules':
                self.read_rules(call.message)
            elif call.data in ['/retailer', '/distributor', '/wholesaler', '/giant_wholesaler', '/manufacturer']:
                self.set_the_player(call)
            elif call.data == 'restart_the_game':
                self.restart_the_game()
        else:
            print(call.message)

    def start_the_game(self, message):
        if message.chat.id not in self.players and self.status != (self.n_users + 1):
            bt_player_role = ['Retailer', 'Distributor', 'Wholesaler', 'Giant Wholesaler',  'Manufacturer']

            self.make_inline_buttons(message, bt_player_role[:self.n_users], "Who are you in that retail chain?", 2)
        elif message.chat.id not in self.players and self.status == (self.n_users + 1):
            if message.chat.id != self.admin:
                self.bot.send_message(message.chat.id, "Sorry game is already began, try it later\n")
            else:
                self.bot.send_message(message.chat.id, "Do you want to restart the game?\n")
                bt_restart = ['Restart the Game', 'Start']
                self.make_inline_buttons(message, bt_restart, "What do you want me to do?", 1)
        else:
            self.continue_the_game(message, 0)

    def set_the_player(self, call):
        cl_player_role = ['/retailer', '/distributor', '/wholesaler', '/giant_wholesaler', '/manufacturer']
        cl_player_role = self.mk_player_role(cl_player_role)
        if call.message.chat.id not in self.players:
            if call.data == '/retailer':
                if self.players[0] == 0:
                    self.players[0] = call.message.chat.id
                    self.continue_the_game(call.message, 0)
                else:
                    self.bot.send_message(call.message.chat.id, 'Someone chose this part of the chain, try another')
            elif call.data == '/manufacturer':
                if self.players[self.n_users - 1] == 0:
                    self.players[self.n_users - 1] = call.message.chat.id
                    self.continue_the_game(call.message, 0)
                else:
                    self.bot.send_message(call.message.chat.id, 'Someone chose this part of the chain, try another')
            else:
                if self.players[cl_player_role.index(call.data) - 1] == 0:
                    self.players[cl_player_role.index(call.data) - 1] = call.message.chat.id
                    self.continue_the_game(call.message, 0)
                else:
                    self.bot.send_message(call.message.chat.id, 'Someone chose this part of the chain, try another')
        else:
            self.bot.send_message(call.message.chat.id, "You are playing the Game. Just wait for")

        print(self.players)

    def mk_player_role(self, player_role):


    def restart_the_game(self):
        return

    def continue_the_game(self, message, waiting_time):
        if self.status < self.n_users:
            if waiting_time > 120:
                self.restart_the_game
            time.sleep(3)
            waiting_time += 3
            self.continue_the_game(message, waiting_time)
        elif self.status == self.n_users:
            self.status += 1
            for tmp in self.players:
                self.bot.send_message(tmp, 'Beer Game Beginning R')

    def read_rules(self, message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="Show me the rules", url="https://google.com"))
        self.bot.send_message(message.chat.id, "You can push button bellow and find rules.", reply_markup=markup)

    # First message you get when you came to Bot
    def start_message(self, message):
        pr_start_actions = False
        if self.status == 0:
            pr_start_actions = True
            self.bot.send_message(chat_id=message.chat.id,\
                                  text='Hi, I am BeerGame_Bot. With my help you can play popular Beer Game.\n'
                                       'Join our Beer Game! You will be the first!\n')
        elif 0 < self.status < self.n_users:
            if message.chat.id not in self.players:
                pr_start_actions = True
                self.bot.send_message(chat_id=message.chat.id,\
                                      text='Hi, I am BeerGame_Bot. With my help you can play popular Beer Game!\n'
                                           'Join Beer Game. We need only ' + str(self.n_users - self.status) +
                                           ' players.')
            else:
                self.start_the_game(message)
        elif self.status == self.n_users + 1:
            if message.chat.id not in self.players:
                self.bot.send_message(chat_id=message.chat.id,\
                                      text='Hi, I am BeerGame_Bot. With my help you can play popular Beer Game!\n'
                                           'Unfortunately Beer Game has began without you, try it later\n')
        if pr_start_actions:
            bt_start_actions = ['Help', 'Read rules', 'Start the Game']
            self.make_inline_buttons(message, bt_start_actions, "What do you want me to do?", 1)

        print(message.chat.id,'\n')

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


New_Session = BeerGameBot()
New_Session.bot.polling()
