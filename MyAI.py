# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		
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
		self.effective_num = None
		self.locals = None
		self.normalized_weighted_num = None  # = (num - adjacent flags) / adjacent hidden cells
		self.mine_probability = None
		self.is_dead = False
		self.rec_perm_value = 0
		self.temp_is_mine = False

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

		# if the cell is revealed (self.num is not None) and has adjacent unflagged hidden cells, calculate its
		# normalized weight value ((num - adjacent flags) / adjacent hidden cells)
		if self.num is not None and len(unflagged_hidden_locals) > 0:
			self.effective_num = self.num - len(flagged_locals)
			self.normalized_weighted_num = self.effective_num / len(unflagged_hidden_locals)

		# if cell is hidden and has at least 1 adjacent revealed cell, calculate mine probability heuristic
		if not self.revealed and not self.flag and len(hidden_locals) < len(self.locals):
			sum = 0
			for cell in self.locals:
				if cell.normalized_weighted_num is not None:
					sum += cell.normalized_weighted_num
			'''
			if len(self.locals) < 8:
				if len(self.locals) < 5:
					sum += self._CORNER_WEIGHT
				else:
					sum += self._EDGE_WEIGHT
			'''
			self.mine_probability = sum / len(self.locals)
			self.board.frontier.add(self) # add this cell to the frontier

		elif self in self.board.frontier:
			# if this cell no longer satisfies the first if condition, it should not be in the frontier
			self.board.frontier.remove(self)

		# If there are no remaining uncovered, unflagged cells around this cell, we don't care about this cell
		if len(hidden_locals) == len(flagged_locals) and self not in self.board.frontier:
			self.is_dead = True
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

	def get_frontier_locals(self):
		return self.locals.intersection(self.board.frontier)

	def get_revealed_locals(self):
		return self.locals.difference(self.get_hidden_locals())

	def check_local_mine_configuration(self):
		num_mines = 0
		for cell in self.locals:
			if cell.temp_is_mine:
				num_mines += 1

		if num_mines > self.effective_num:
			return -1
		elif num_mines == self.effective_num:
			return 1
		else:
			return 0

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

	def print_cell(self, end='\n'):
		#print(self.__str__() + f": {self.x},{self.y}", end=end)
		pass

	def coords_to_str(self):
		#return f"({self.x}. {self.y})"
		pass


class Board:
	def __init__(self, rowDimension, colDimension, mineTotal):
		self.board = []
		self.rows = colDimension
		self.cols = rowDimension
		self.remaining_cells = set()
		self.init_board(self.rows, self.cols)
		self.remaining_mines = mineTotal
		self.past_cells = set()
		self.frontier = set()
		self.permutations = 0
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
		print("     ", end='')
		for y in range(self.cols):
			print("{0: <4d}".format(y), end='')
		print()
		for x in range(self.rows):
			print("{0: <2d}: [".format(x), end='')
			for y in range(self.cols):
				print(self.board[x][y], end='')
				if y != self.cols - 1:
					print(', ', end='')
			print("]")

	def print_board_coords(self):
		for x in range(self.rows):
			print("[", end='')
			for y in range(self.cols):
				cell = self.get_cell(x, y)
				cell.print_cell('')
				if y != self.cols - 1:
					print(', ', end='')
			print("]")


	def get_remaining_unflagged_hidden_cells(self):
		cells = set()
		for x in range(self.rows):
			for y in range(self.cols):
				cell = self.get_cell(x,y)
				if cell.flag is False and cell.revealed is False:
					cells.add(cell)

		return cells


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		self.Board = Board(rowDimension, colDimension, totalMines)
		self.prevX = startX
		self.prevY = startY
		self.possibleMoves = set()
		self.riskyMoves = set()
		self.DEBUG = False
		self.FULL_DEBUG = False
		self.CSP_DEPTH_LIMIT = 30

		cell = self.Board.get_cell(startX, startY)

		if self.DEBUG:
			print(startX, startY)
			self.Board.print_board_coords()
			print()
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################


	def getAction(self, number: int) -> "Action Object":

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		prev_cell = self.Board.get_cell(self.prevX, self.prevY)

		# updates the cell from the previous move
		if number > -1:
			if self.DEBUG:
				#print(f"Setting previous cell {self.prevX}, {self.prevY} to revealed")
				pass
			prev_cell.reveal()
			prev_cell.set_num(number)
		else:
			if self.DEBUG:
				#print(f"Setting previous cell {self.prevX}, {self.prevY} to flagged")
				pass
			prev_cell.toggle_flag()
			self.Board.remaining_mines -= 1

		if self.DEBUG:
			# prints board for debugging
			#print(f"Remaining mines: {self.Board.remaining_mines} | Remaining cells: {len(self.Board.remaining_cells)}")
			self.Board.print_board()
			print()

		# checks mine count to see if all have been found
		if self.Board.remaining_mines == 0:
			cells = self.Board.get_remaining_unflagged_hidden_cells()
			if len(cells) == 0:
				if self.DEBUG:
					print("LEAVING")
				return Action(AI.Action.LEAVE)

			for cell in cells:
				self.possibleMoves.add(("R", cell))

		# checks queue of known moves
		if len(self.possibleMoves) > 0:
			act, cell = self.possibleMoves.pop()
			return self.create_action(act, cell)

		# adds moves to queue based on logical rules
		self.add_possible_moves_to_queue()

		# checks queue again in case moves were added from logical rules
		if len(self.possibleMoves) > 0:
			act, cell = self.possibleMoves.pop()
			return self.create_action(act, cell)

		if self.FULL_DEBUG:
			input("Press any key to continue to CSP heuristic\n")

		# do CSP heuristic (no moves were in queue even after logical rules)
		if self.DEBUG:
			print("Doing CSP heuristic")

		islands, num_frontiers = self.CSP_setup()
		moves = []
		for i in range(len(islands)):
			if len(islands[i]) <= self.CSP_DEPTH_LIMIT:
				if self.DEBUG:
					#print(f"Doing CSP heuristic for island {i}")
					pass
				moves += self.do_CSP_heuristic(self.FULL_DEBUG, islands[i], num_frontiers[i])
			elif self.DEBUG:
				#print(f"Skipped CSP heuristic for island {i}")
				pass

		moves.sort(key=lambda x: x[0])  # sorts moves with smallest probability first
		if self.DEBUG:
			#print(f"CSP Heuristic result: {moves}")
			pass

		if moves:
			small = moves[0][0]

			for prob, cell in moves:
				if prob == small:
					if small == 0:
						self.possibleMoves.add(("R", cell))
					else:
						self.riskyMoves.add(("R", cell))

			# check for moves in queue again (CSP heuristic adds moves to queue)
			if len(self.possibleMoves) > 0:
				act, cell = self.possibleMoves.pop()
				return self.create_action(act, cell)

			# at this point, safety is not guaranteed
			while len(self.riskyMoves) > 0:
				act, cell = self.riskyMoves.pop()
				try:
					return self.create_action(act, cell)
				except KeyError:
					continue


		if self.DEBUG:
			print("CSP yielded no results because island sizes exceeded depth limit")

		# do mine probability heuristic
		if self.DEBUG:
			print("Doing mine probability heuristic")
		move = self.create_action("R", self.mine_probability_heuristic())

		if move is None:
			if self.Board.remaining_mines == len(self.Board.remaining_cells):
				self.queue_remaining_cells("F")
			elif self.Board.remaining_mines == 0:
				self.queue_remaining_cells("R")
			else:
				if self.DEBUG:
					print("ENCOUNTERED PURE CHANCE SCENARIO")
				self.queue_remaining_cells("R")

			if len(self.possibleMoves) > 0:
				act, cell = self.possibleMoves.pop()
				return self.create_action(act, cell)
		else:
			return move



		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

	def create_action(self, act, cell):
		if cell is None:
			return None

		self.prevX = cell.x
		self.prevY = cell.y
		self.Board.remaining_cells.remove(cell)
		self.Board.past_cells.add(cell)
		if act == "F":
			if self.DEBUG:
				#print(f"Flagging {cell.x}, {cell.y}")
				pass
			return Action(AI.Action.FLAG, cell.x, cell.y)
		if act == "R":
			if self.DEBUG:
				#print(f"Revealing {cell.x}, {cell.y}")
				pass
			return Action(AI.Action.UNCOVER, cell.x, cell.y)

	def add_possible_moves_to_queue(self):
		for x in range(self.Board.rows):
			for y in range(self.Board.cols):
				cur_cell = self.Board.get_cell(x, y)
				if not cur_cell.is_dead:
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

	def CSP_setup(self):
		islands = self.separate_frontier_islands(self.Board.frontier)
		num_frontiers = []

		if self.DEBUG:
			for i, f in enumerate(islands):
				#print(f"Frontier {i}: {len(f)}")
				pass

		# numeric frontier is a set of revealed (numbered) cells adjacent to any frontier cell
		numeric_frontier = set()

		# fills numeric frontier with the proper cells
		for f in islands:
			for cell in f:
				for num_cell in cell.get_revealed_locals():
					numeric_frontier.add(num_cell)
			num_frontiers.append(numeric_frontier.copy())
			numeric_frontier.clear()

		return islands, num_frontiers

	def do_CSP_heuristic(self, debug, frontier, numeric_frontier):
		# mine_set is the set of temporarily-placed mines
		# this is the actual recursive part
		zeroDivFlag = False
		self.Board.permutations = 0
		frontier_copy = frontier.copy()
		for cell in frontier:
			mines_set = set()
			mines_set.add(cell)
			frontier_copy.remove(cell)
			if debug:
				print("Beginning recursion")
			self._recursive_CSP(cell, frontier_copy, numeric_frontier.copy(), mines_set, 0, debug)

		# determines smallest permutation value
		smallest = 1000  # this number is arbitrary, it just needs to be big
		for cell in frontier:
			if cell.rec_perm_value < smallest:
				smallest = cell.rec_perm_value

		# gets the frontier cell with the lowest number of valid configurations in which it had a mine
		# (the smallest permutation value)
		moves = []
		for cell in frontier:
			if cell.rec_perm_value == smallest:
				try:
					moves.append((cell.rec_perm_value / self.Board.permutations, cell))
				except ZeroDivisionError:
					zeroDivFlag = True

			# resets the temp attributes used for the recursive heuristic
			cell.rec_perm_value = 0
			cell.temp_is_mine = False

		if zeroDivFlag:
			return list()
		else:
			return moves

	def _recursive_CSP(self, cell, remaining, num_cells, mines, depth, debug):
		'''Recursively searches the state space of the frontier nodes, avoiding obviously impossible states'''

		if debug or (self.DEBUG and depth == 0):
			#print(("\t" * depth) + f"rCSP(c:{cell.coords_to_str()}, r:{len(remaining)}, nc:{len(num_cells)}, m:{len(mines)}, d:{depth})")
			pass

		# Begin by assuming 'cell' is a mine
		cell.temp_is_mine = True

		# removed is the set of frontier cells that cannot be assigned mines in this configuration so far
		removed = set()
		# removed_nums is the set of numbered cells that have been satisfied
		removed_nums = set()

		# iterates through numbered cells and checks if they're satisfied
		for num_cell in cell.get_revealed_locals():  # CHANGE: "in num_cells.copy()" -> "cell.get_revealed_locals()"
			result = num_cell.check_local_mine_configuration()
			if result == -1:
				# num cell has more adjacent bombs than its number indicates; this is a bad board configuration
				cell.temp_is_mine = False
				return
			elif result == 1:
				# num cell is satisfied
				removed_nums.add(num_cell)  # add this numbered cell to removed_nums; it's now satisfied
				flocals = num_cell.get_frontier_locals()  # gets the frontier cells local to the satisfied num cell
				removed = removed.union(flocals)  # adds those aforementioned frontier cells to the removed set
			else:
				# num cell is not satisfied; this is an incomplete board configuration
				pass

		if not remaining.difference(removed) and not num_cells.difference(removed_nums):
			# found valid board state; increment the permutation value of each cell assumed to be a mine in this board
			for bcell in mines:
				bcell.rec_perm_value += 1

				if debug:
					print("Mine cell:", end='')
					bcell.print_cell()

			cell.temp_is_mine = False
			self.Board.permutations += 1
			return

		# iterates through remaining frontier cells (those not adjacent to satisfied num cells)
		# then recursively calls (exploring board configurations where that cell is a mine)
		new_remaining = remaining.difference(removed)
		for new_cell in remaining.difference(removed):
			new_remaining.remove(new_cell)
			new_cell_set = set()
			new_cell_set.add(new_cell)
			self._recursive_CSP(new_cell, new_remaining.copy(),
								num_cells.copy().difference(removed_nums), mines.copy().union(new_cell_set), depth + 1, debug)


		cell.temp_is_mine = False
		return


	def separate_frontier_islands(self, frontier):
		islands = []
		visited = set()
		queue = set()
		temp = frontier.copy()

		while temp:
			visited.clear()
			'''
			cell = temp.pop()
			visited.add(cell)
			flocals = cell.get_frontier_locals()
			queue = queue.union(flocals)
			temp = temp.difference(flocals)
			'''
			queue.add(temp.pop())
			while queue:
				cell = queue.pop()
				visited.add(cell)
				flocals = cell.get_frontier_locals()
				queue = queue.union(flocals.difference(visited))
				temp = temp.difference(flocals)
			islands.append(visited.copy())

		return islands
