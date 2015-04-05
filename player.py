import random
from bet import Bet
from bet import DUDO
from bet import create_bet
from bet_exceptions import BetException
from bet_exceptions import InvalidDieValueException
from bet_exceptions import NonPalificoChangeException
from bet_exceptions import InvalidNonWildcardQuantityException
from bet_exceptions import InvalidWildcardQuantityException
from bet_exceptions import InvalidBetException
from die import Die
from math import floor
from math import ceil
from strings import BAD_BET_ERROR
from strings import INVALID_DIE_VALUE_ERROR
from strings import NON_PALIFICO_CHANGE_ERROR
from strings import INVALID_NON_WILDCARD_QUANTITY
from strings import INVALID_WILDCARD_QUANTITY
from strings import INVALID_BET_EXCEPTION

class Player(object):

	def __init__(self, name, dice_number, game):
		self.name = name
		self.game = game
		self.palifico_round = -1
		self.dice = []
		for i in range(0, dice_number):
			self.dice.append(Die())

	def make_bet(self, current_bet):
		pass

	def roll_dice(self):
		for die in self.dice:
			die.roll()
		# Sort dice into value order e.g. 4 2 5 -> 2 4 5
		self.dice = sorted(self.dice, key=lambda die: die.value)

	def count_dice(self, value):
		number = 0
		for die in self.dice:
			if die.value == value or (not self.game.is_palifico_round() and die.value == 1):
				number += 1
		return number

class ComputerPlayer(Player):

	def make_bet(self, current_bet):
		total_dice_estimate = len(self.dice) * len(self.game.players)
		if current_bet is None:
			# CPU is the first player, so make a conservative estimate
			value = random.choice(self.dice).value
			quantity_limit = (total_dice_estimate - len(self.dice))/6
			if value > 1:
				quantity_limit *= 2
			quantity = self.count_dice(value) + random.randrange(0, quantity_limit + 1)
			bet = create_bet(quantity, value, current_bet, self, self.game)
		else:
			# Estimate the number of dice in the game with the bet's value
			if current_bet.value == 1 or self.game.is_palifico_round():
				# There should be twice as many of any value than 1
				limit = ceil(total_dice_estimate/6.0) + random.randrange(0, ceil(total_dice_estimate/4.0))
			else:
				limit = ceil(total_dice_estimate/6.0) * 2 + random.randrange(0, ceil(total_dice_estimate/4.0))
			if current_bet.quantity >= limit:
				return DUDO
			else:
				bet = None
				while bet is None:
					if self.game.is_palifico_round() and self.palifico_round == -1:
						# If it is a Palifico round and the player has not already been palifico,
						# the value cannot be changed.
						value = current_bet.value
						quantity = current_bet.quantity + random.randrange(0, 2)
					else:
						value = random.choice(self.dice).value
						if value == 1:
							if current_bet.value > 1:
								quantity = int(ceil(current_bet.quantity/2.0))
							else:
								quantity = current_bet.quantity + random.randrange(0, 2)
						else:
							if current_bet.value == 1:
								quantity = current_bet.quantity * 2 + 1
							else:
								quantity = current_bet.quantity + random.randrange(0, 2)
					try:
						bet = create_bet(quantity, value, current_bet, self, self.game)
					except BetException:
						bet = None

		return bet

class HumanPlayer(Player):

	def make_bet(self, current_bet):
		string = 'Your turn. Your dice:'
		for die in self.dice:
			string += ' {0}'.format(die.value)
		print string
		bet = None
		while bet is None:
			bet_input = raw_input('> ')
			if bet_input.lower() == 'dudo':
				return DUDO
			if 'x' not in bet_input:
				self.print_bad_bet_error()
				continue
			bet_fields = bet_input.split('x')
			if len(bet_fields) < 2:
				self.print_bad_bet_error()
				continue

			try:
				quantity = int(bet_fields[0])
				value = int(bet_fields[1])

				try:
					bet = create_bet(quantity, value, current_bet, self, self.game)
				except InvalidDieValueException:
					bet = None
					print INVALID_DIE_VALUE_ERROR
				except NonPalificoChangeException:
					bet = None
					print NON_PALIFICO_CHANGE_ERROR
				except InvalidNonWildcardQuantityException:
					bet = None
					print INVALID_NON_WILDCARD_QUANTITY
				except InvalidWildcardQuantityException:
					bet = None
					print INVALID_WILDCARD_QUANTITY
				except InvalidBetException:
					bet = None
					print INVALID_BET_EXCEPTION
			except ValueError:
				print BAD_BET_ERROR

		return bet