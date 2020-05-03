# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action


class Cell:
	_CORNER_WEIGHT = .5
	_EDGE_WEIGHT = .3

	def __init__(self, board, x, y):
		self.board = board
		self.x = x
		self.y = y
		self.flag = False
		self.revealed = False
		self.num = None
		self.locals = None
		self.normalized_weighted_num = None  # = (num - adjacent flags) / adjacent hidden cells
		self.mine_probability = None

	def toggle_flag(self):
		self.flag = not self.flag

	def reveal(self):
		self.revealed = True

	def set_num(self, num):
		self.num = num

	def do_logical_rules(self):
		hidden_locals = self.get_hidden_locals()
		flagged_locals = self.get_flagged_locals()
		unflagged_locals = self.locals.difference(flagged_locals)
		unflagged_hidden_locals = hidden_locals.intersection(unflagged_locals)

		if self.num is not None and len(unflagged_hidden_locals) > 0:
			self.normalized_weighted_num = (self.num - len(flagged_locals)) / len(unflagged_hidden_locals)

		# if cell is hidden and has at least 1 adjacent revealed cell
		if not self.revealed and len(hidden_locals) < len(self.locals):
			sum = 0
			for cell in self.locals:
				if cell.normalized_weighted_num is not None:
					sum += cell.normalized_weighted_num
			if len(self.locals) < 8:
				if len(self.locals) < 5:
					sum += self._CORNER_WEIGHT
				else:
					sum += self._EDGE_WEIGHT
			self.mine_probability = sum

		# If there are no remaining uncovered, unflagged cells around this cell, we don't care about this cell
		if len(hidden_locals) == len(flagged_locals):
			return "N", set()

		# If the number of uncovered cells around a cell equals that cell's number, each uncovered cell is a bomb
		# (and should therefore be flagged)
		if len(hidden_locals) == self.num:
			return "F", unflagged_hidden_locals

		# If the number of flagged cells around a cell equals that cell's number, each unflagged cell can be revealed
		if len(flagged_locals) == self.num:
			return "R", unflagged_hidden_locals

		# If none of the above conditions are true, this simple algorithm cannot learn anything from this cell
		return "N", set()

	def get_hidden_locals(self):
		filtered = set()
		for cell in self.locals:
			if not cell.revealed:
				filtered.add(cell)

		return filtered

	def get_flagged_locals(self):
		filtered = set()
		for cell in self.locals:
			if cell.flag:
				filtered.add(cell)

		return filtered

	def set_locals(self):
		locals = set()
		locals.add(self._N())
		locals.add(self._NE())
		locals.add(self._NW())
		locals.add(self._E())
		locals.add(self._W())
		locals.add(self._S())
		locals.add(self._SW())
		locals.add(self._SE())

		try:
			locals.remove(None)
		except KeyError:
			pass

		self.locals = locals

	def _N(self):
		return self.board.get_cell(self.x, self.y-1)

	def _NW(self):
		return self.board.get_cell(self.x-1, self.y-1)

	def _NE(self):
		return self.board.get_cell(self.x+1, self.y-1)

	def _E(self):
		return self.board.get_cell(self.x+1, self.y)

	def _W(self):
		return self.board.get_cell(self.x-1, self.y)

	def _S(self):
		return self.board.get_cell(self.x, self.y+1)

	def _SW(self):
		return self.board.get_cell(self.x-1, self.y+1)

	def _SE(self):
		return self.board.get_cell(self.x+1, self.y+1)

	def __str__(self):
		if self.num is not None:
			return str(self.num) + ' '
		elif self.flag:
			return "F" + ' '
		else:
			return "[]"

class Board:
	def __init__(self, rowDimension, colDimension, mineTotal):
		self.board = []
		self.rows = rowDimension
		self.cols = colDimension
		self.remaining_cells = set()
		self.init_board(rowDimension, colDimension)
		self.remaining_mines = mineTotal
		# self.print_board()

	def init_board(self, rowDimension, colDimension):
		for x in range(rowDimension):
			self.board.append([])

			for y in range(colDimension):
				self.board[x].append(Cell(self, x, y))

		self.init_cells()

	def get_cell(self, x, y):
		if (x < 0 or x > len(self.board) - 1) or (y < 0 or y > len(self.board[0]) - 1):
			return None
		else:
			return self.board[x][y]

	def init_cells(self):
		for x in range(self.rows):
			for y in range(self.cols):
				self.board[x][y].set_locals()
				self.remaining_cells.add(self.board[x][y])

	def print_board(self):
		for x in range(self.rows):
			print("[", end='')
			for y in range(self.cols):
				print(self.board[x][y], end='')
				if y != self.cols - 1:
					print(', ', end='')
			print("]")


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		self.Board = Board(rowDimension, colDimension, totalMines)
		self.prevX = startX
		self.prevY = startY
		self.possibleMoves = set()

		cell = self.Board.get_cell(startX, startY)
		# print(startX, startY)
		# print(cell)
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

		
	def getAction(self, number: int) -> "Action Object":

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		prev_cell = self.Board.get_cell(self.prevX, self.prevY)

		if number > -1:
			# print(f"Setting previous cell {self.prevX}, {self.prevY} to revealed")
			prev_cell.reveal()
			prev_cell.set_num(number)
		else:
			# print(f"Setting previous cell {self.prevX}, {self.prevY} to flagged")
			prev_cell.toggle_flag()
			self.Board.remaining_mines -= 1

		# self.Board.print_board()
		# print()

		if len(self.possibleMoves) > 0:
			act, cell = self.possibleMoves.pop()
			return self.create_action(act, cell)

		self.add_possible_moves_to_queue()

		if len(self.possibleMoves) > 0:
			act, cell = self.possibleMoves.pop()
			return self.create_action(act, cell)

		move = self.create_action("R", self.mine_probability_heuristic())

		if move is None:
			if self.Board.remaining_mines == 0:
				return Action(AI.Action.LEAVE)
			else:
				if self.Board.remaining_mines == len(self.Board.remaining_cells):
					self.queue_remaining_cells("F")
				elif self.Board.remaining_mines == 0:
					self.queue_remaining_cells("R")
				else:
					# print("ENCOUNTERED PURE CHANCE SCENARIO")
					self.queue_remaining_cells("R")

				if len(self.possibleMoves) > 0:
					act, cell = self.possibleMoves.pop()
					return self.create_action(act, cell)
		else:
			return move


		# print("LOGICAL RULES DID NOT FIND AVAILABLE MOVES")


		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

	def create_action(self, act, cell):
		if cell is None:
			return None

		self.prevX = cell.x
		self.prevY = cell.y
		self.Board.remaining_cells.remove(cell)
		if act == "F":
			# print(f"Flagging {cell.x}, {cell.y}")
			return Action(AI.Action.FLAG, cell.x, cell.y)
		if act == "R":
			# print(f"Revealing {cell.x}, {cell.y}")
			return Action(AI.Action.UNCOVER, cell.x, cell.y)

	def add_possible_moves_to_queue(self):
		for x in range(self.Board.rows):
			for y in range(self.Board.cols):
				act, possible_moves = self.Board.get_cell(x, y).do_logical_rules()
				if len(possible_moves) > 0:
					for cell in possible_moves:
						self.possibleMoves.add((act, cell))

	def mine_probability_heuristic(self):
		'''Returns a cell with the lowest probability of having a mine'''
		cell = self.get_first_unflagged_hidden_cell()
		for ncell in self.Board.remaining_cells:
			if ncell.mine_probability is not None and cell.mine_probability > ncell.mine_probability:
				cell = ncell

		return cell

	def get_first_unflagged_hidden_cell(self):
		for cell in self.Board.remaining_cells:
			if cell.mine_probability is not None:
				return cell

	def queue_remaining_cells(self, action):
		for cell in self.Board.remaining_cells:
			self.possibleMoves.add((action, cell))
