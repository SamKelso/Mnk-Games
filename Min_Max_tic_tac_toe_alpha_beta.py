import numpy as np
from Buffer import Store_State_Values_Buffer
import random
import numpy as np
import time





class Game(object):

	def __init__(self,m,n,k,human_players = [1],computer_player = [1, 2],display = True):

		self.m = m #Number of columns on the board
		self.n=n #Number of rows on the board
		self.k=k #Number of 'X's or "O"s required to win the game
		self.human_players = human_players
		self.computer_player = computer_player
		self.state = (set(), set()) #stores the moves made by player 1 and player 2
		self.a_v = {}
		self.display = display
		self.stored_states=0
		self.possible_moves ={(x,y) for x in range(1,self.m+1) for y in range(1, self.n+1)}
		self.directions =(self.horizontal, self.right_diagonal, self.vertical, self.left_diagonal)
		self.state_buffer = Store_State_Values_Buffer() 
		self.a_v = {}


	def initialize_game(self):
		"""
		intializes board based on board dimensions m and n.
		"""
		return [[' ' for i in range(self.m)] for i in range(self.n)]
		




	def drawboard(self,state):

		"""
		The draw_board function graphically represents the board based on the dimensions initalized

		Example:
			A   B   C 
		  -------------
		3 |   |   |   | 3
		  -------------
		2 |   |   |   | 2
		  -------------
		1 |   |   |   | 1
		  -------------
			A   B   C 
		
		Arg- State(set) the tuple of 2 set()'s which stores all moves of player 1 and 2

		returns board(string)

		"""
		array_board=self.initialize_game()  #Creates the array_board by calling initialize_game()
		for x, y in state[0]:
			array_board[self.n - y][x - 1] = 'X'
		for x, y in state[1]:
			array_board[self.n - y][x - 1] = 'O'

		board_lines_list = []
		#the Column labels provide the column co-ordinates to help the player chose the column he/she wishes to place 'X'
		# [A B C] are the column labels as shown above
		Reset_alphabets = 64

		Column_labels =(' ' * (len(str(self.n)) + 3) +(' ' * 3).join([chr(code + Reset_alphabets) for code in range(1, self.m + 1)]) + ' \n')

		for idx, array_line in enumerate(array_board, 1):
			idx = self.n + 1 - idx
			number_spaces_before_line = len(str(self.n)) - len(str(idx))
			space_before_line = number_spaces_before_line * ' '
			board_lines_list.append(f'{space_before_line}{idx} | ' +' | '.join(array_line) + f' | {idx}\n')
		line_dashes = (len(str(self.n)) + 1)*' ' + '-' * 4 * self.m + '-\n'
		board_design = Column_labels + line_dashes + line_dashes.join(board_lines_list) +line_dashes + Column_labels

		print(board_design)

	def is_terminal(self, state, last_action, player):
		"""
		The _is_terminal function checks if a game has ended by achieving the target k. 
		This function takes in the player who took the last action and the last action taken
		by the last player. This is to speed up the process time by looking only for the actions 
		taken bu the last player and determining if it is a terminal state or not 
  
		Args:

		 	state(tuple(set(),set()): Tuple consisting of moves stored of each player

			last_action (tuple(int,int)): Coorindates of the last action taken in the game.

			player (int): The player who made the last move.

		return: 

			(Terminal,winner): (boolean,int)
							 : Terminal= True, if state=Terminal
							 : Terminal= False, if state !=Terminal
							 : winner = Player [1,2] who played the last move and  Terminal =True

		"""
		#initalize the output variables
		terminal = False
		winner = None


		#check if there are no more actions available i.e. the board is full
		if last_action == None:
			return terminal, winner

		stored_moves = state[player - 1]

		for direction in self.directions:
			count_k = 1 #counts the number 
			step_direction = 1 


			while True:
				if direction(last_action[0], last_action[1], step_direction) in stored_moves:
					count_k += 1
					step_direction += 1
				else:# when the player does not occupy the cell, break the loop
					break

			step_direction = -1#check the other way
			while True:
				if direction(last_action[0], last_action[1], step_direction) in stored_moves:#player also occupies this cell
					count_k += 1
					step_direction -= 1
				else:# when the player does not occupy the cell, break the loop
					break

			if count_k >= self.k: # If the number of K values = the intialized self.k, then player wins
				terminal = True
				winner = player
				break

		total_moves=len(state[0]) + len(state[1]) #Count the total moves made by each player

		if total_moves == self.n*self.m and not terminal:# if  total moves = area of board, then it is a tie
			winner = 0 #There is no winner
			terminal = True

		return terminal, winner

	def max_(self, state, last_action, search_depth, player=2):

		"""
		Calculates the max value of player 1 for a given state.
		State values are stored in the buffer class. This is done to recall values of already seen
		states. This code addition was implemented to improve computation speed.
		
		Args:

			state(tuple(set(),set()): Tuple consisting of moves stored of each player.


		 	last_action (tuple(int,int)): Coorindates of the last action taken by 
						opposing player in the game. This is done to speed up computational speed.

			search_depth (int): Tracks recursion depth to store state values.  

			player (int): Player 2. Required for terminal calculation

		return:
			v (float): The maximum action value.
	   """
	   # Check if a terminal state has been reached and if so retrun the outcome of the game.
		terminal, winner = self.is_terminal(state, last_action, player)
		if terminal:
			if winner == 1:
				return 1

			if winner == 2:
				return -1

			if winner == 0:
				return 0


		v = -float('inf') #Initialize v as negative infinity 

		# Check if this state value has been previously calculated.
		v_buffer = self.state_buffer.find_value(state)
		if v_buffer == None:
			pass
		elif v_buffer != None:
			return v_buffer


		actions=self.possible_moves - state[0] - state[1]
		# Loop through possible actions.
		for action in actions:

			new_state = self.end_state(state, action, 1)
			self.stored_states=self.stored_states+1
			# Apply Min value function to next layer of nodes.
			v_new = self.min_(new_state, action, search_depth + 1)
			v = max(v, v_new)
			if search_depth == 0:
				self.a_v[action] = v_new
		# Add to calculated state values.
		self.state_buffer.add(state, v)
		return v

	
	def min_(self, state, last_action, search_depth, player=1):

		terminal, winning_player = self.is_terminal(state, last_action, player)
		v = float('inf')
		# Check if a terminal state has been reached and if so retrun the outcome of the game.
		if terminal:
			if winning_player == 1:
				return 1
			elif winning_player == 2:
				return -1
			elif winning_player == 0:
				return 0

		v = float('inf')
		# Check if this state value has been previously calculated.
		v_buffer = self.state_buffer.find_value(state)
		if v_buffer == None:
			pass
		elif v_buffer != None:
			return v_buffer

		actions=self.possible_moves - state[0] - state[1]
		# Loop through possible actions.
		for action in actions:
			new_state = self.end_state(state, action, 2)
			# Apply max value search function to next layer.
			v_new = self.max_(new_state, action, search_depth + 1)
			self.stored_states=self.stored_states+1

			v = min(v, v_new)
			if search_depth == 0:
				self.a_v[action] = v_new
		# Add to calculated state values.
		self.state_buffer.add(state, v)
		return v

	def max_ab(self, state, last_action, search_depth, player=2, alpha=-float('inf'), beta=float('inf')):

		"""
		Calculates the max value of player 1 for a given state.
		State values are stored in the buffer class. This is done to recall values of already seen
		states. This code addition was implemented to improve computation speed.
		
		Args:

			state(tuple(set(),set()): Tuple consisting of moves stored of each player.


		 	last_action (tuple(int,int)): Coorindates of the last action taken by 
						apposing player in the game. This is done to speed up computational speed.

			search_depth (int): Tracks recursion dept to store state values.  

			player (int): Player 2. Required for terminal calculation

		return:
			v (float): The maximum action value.
	   """
	   # Check if a terminal state has been reached and if so retrun the outcome of the game.
		terminal, winner = self.is_terminal(state, last_action, player)
		if terminal:
			if winner == 1:
				return 1

			if winner == 2:
				return -1

			if winner == 0:
				return 0


		v = -float('inf') #Initialize v as negative infinity 

		# Check if this state value has been previously calculated.
		v_buffer, pruned = self.state_buffer.find_value_ab(state)
		if v_buffer == None:
			pass
		elif v_buffer != None and not pruned:
			return v_buffer
		elif v_buffer != None and pruned:
			# In the case where the node has been pruned.
			if v_buffer >= beta:
				return v_buffer


		actions=self.possible_moves - state[0] - state[1]
		# Loop through possible actions.
		for action in actions:
			self.stored_states=self.stored_states+1

			new_state = self.end_state(state, action, 1)

			v_new = self.min_ab(new_state, action, search_depth + 1, alpha=alpha, beta=beta)
			v = max(v, v_new)
			if search_depth == 0:
				if(action in self.a_v):
					self.a_v[action][0] = v_new
				else:
					self.a_v[action] = [v_new, False]
			# Perform relevant update to alpha if valid.
			if(v >= beta):
				self.state_buffer.add_ab(state, v, True)
				if search_depth == 1:
					self.a_v[last_action] = [None, True]
				return v
			alpha = max(alpha, v)
		# Add value to calculated states
		self.state_buffer.add_ab(state, v, False)
		return v

	
	def min_ab(self, state, last_action, search_depth, player=1, alpha=-float('inf'), beta=float('inf')):
		# Check if a terminal state has been reached and if so retrun the outcome of the game.
		terminal, winning_player = self.is_terminal(state, last_action, player)
		v = float('inf')
		if terminal:
			if winning_player == 1:
				return 1
			elif winning_player == 2:
				return -1
			elif winning_player == 0:
				return 0

		v = float('inf')
		# Check if this state value has been previously calculated.
		v_buffer, pruned = self.state_buffer.find_value_ab(state)
		if v_buffer == None:
			pass
		elif v_buffer != None and not pruned:
			return v_buffer
		elif v_buffer != None and pruned:
			# In the case where the node has been pruned.
			if v_buffer >= alpha:
				return v_buffer
		actions = self.possible_moves - state[0] - state[1]
		# Loop through possible actions.
		for action in actions:
			self.stored_states=self.stored_states+1

			new_state = self.end_state(state, action, 2)
			v_new = self.max_ab(new_state, action, search_depth + 1, alpha=alpha, beta=beta)
			v = min(v, v_new)
			if search_depth == 0:
				if(action in self.a_v):
					self.a_v[action][0] = v_new
				else:
					self.a_v[action] = [v_new, False]
			# Perform relevant update to beta if valid.
			if(v <= alpha):
				self.state_buffer.add_ab(state,v, True)
				if search_depth == 1:
					self.a_v[last_action] = [None, True]
				return v
			beta = min(beta, v)
		# Add value to calculated states.
		self.state_buffer.add_ab(state, v, False)
		return v

	def is_valid(self, state, action):
		"""
		The is_valid checks if a given action is allowed for a given state.
		Validity is based on the action being within the boundaries of the board and not 
		occupied.

		Args:
			state (tuple(set(),set()): Tuple consisting of moves stored of each player.
			action (tuple(int, int)): x coordinate represents the projection on the x-axis of board.
									  y coordinate represents the projection on the y-axis of board 


		return: True if action is valid, False if action is invalid.
		"""
		x_range = 1 <= action[0] <= self.m
		y_range = 1 <= action[1] <= self.n

		p1_not_occupied = action not in state[0]
		p2_not_occupied = action not in state[1]


		return(x_range==y_range== p1_not_occupied==p2_not_occupied)



	def end_state(self, state, action, player):
		"""
		Determines the new state for a given action and state.

		Args:
			state (tuple(set(),set()): Tuple consisting of moves stored of each player.
			action (tuple(int, int)): x coordinate represents the projection on the x-axis of board.
									  y coordinate represents the projection on the y-axis of board 

		return: tuple (set(), set()) of the games state.
		"""
		new_state = (state[0].copy(), state[1].copy())

		if player == 1:
			new_state[0].add(action)
			return(new_state[0], new_state[1])

		elif player == 2:
			new_state[1].add(action)
			return(new_state[0], new_state[1])

################################################################################3
#The following are helper functions

	def horizontal(self, x, y, step_size):
		"""
		Find terminal state along the horizontal axis

		Args:
			x (int): Coorindate on x-axis
			y (int): Coorindate on y-axis
			step_size (int): Number of steps taken in the horizontal direction. 
			N.B a negative step_size means moving in the opposite direction

		returns:
			horizontal_check (tuple (int,int)): moves x=step_sizes in horizontal direction

		"""
		horizontal_check= (x+step_size, y)
		return horizontal_check

	def right_diagonal(self, x, y, step_size):
		"""
		Find terminal state along the right diagonal 

		Args:
			x (int): Coorindate on x-axis
			y (int): Coorindate on y-axis
			step_size (int): Number of steps taken along the right diagonal direction. 
			N.B a negative step_size means moving in the opposite direction

		returns:
			right_diagonal_check (tuple (int,int)): moves x=step_sizes in right diagonal direction

		"""
		right_diagonal_check=(x+step_size, y+step_size)
		return right_diagonal_check

	def vertical(self, x, y, step_size):
		"""
		Find terminal state along the vertical axis

		Args:
			x (int): Coorindate on x-axis
			y (int): Coorindate on y-axis
			step_size (int): Number of steps taken along the vertical direction. 
			N.B a negative step_size means moving in the opposite direction

		returns:
			vertical_check (tuple (int,int)): moves x=step_sizes in vertical direction
		"""
		vertical_check=(x, y+step_size)
		return vertical_check

	def left_diagonal(self, x, y, step_size):
		"""
		Find terminal state along the left diagonal 

		Args:
			x (int): Coorindate on x-axis
			y (int): Coorindate on y-axis
			step_size (int): Number of steps taken along the left_diagonal direction. 
			N.B a negative step_size means moving in the opposite direction

		returns:
			left_diagonal_check (tuple (int,int)): moves x=step_sizes in left_diagonal direction
		"""
		left_diagonal_check=(x-step_size, y+step_size)
		return left_diagonal_check


	def array_coordinates_converter(self, arr_coordinates):
		"""
		Convert array[int,int] coordinates to board coordinates:
		eg: [1,1]=[A1]
		This function is used to provide the user with a list of potential options

		Args:
			arr_coordinates (list): list of length 2 consisting of the x and y coordinates

		returns: board_coordinates_str (str): string representing the board coorindates


		"""
		board_coordinates = []
		Reset_alphabets = 64

		for x, y in arr_coordinates:
			x_board = chr(x + Reset_alphabets)
			y_board = str(y)
			board_coordinates.append(x_board + y_board)

		board_coordinates.sort()
		board_coordinates_str = str()


		for coordinate in board_coordinates:
			board_coordinates_str += coordinate + ', '
		return board_coordinates_str[:-2] + '.'

	def board_coordinates_converter(self, board_coordinates):
		"""
		Converts from board coordinates to array coordinates
		eg: A1=[1,1]
		
		This function is used to convert the player input coordinates to array coorindates which can be processed

		Args:
			board_coordinates (str): example: 'A1'

		returns:
			arr_coordinates tuple(int,int): example (1,1)

		"""
		Reset_alphabets = 64

		x_arr = ord(board_coordinates[0].upper()) - Reset_alphabets
		y_arr = int(board_coordinates[1])

		arr_coordinates=(x_arr,y_arr)


		return arr_coordinates


###############################################################################
#Playing the game 

	def minimax_action(self, state, player, ab_prune=False):
		"""
		The minimax algorthim calculates the minimax action for each player
		based on the current moves played i.e. state

		Args:
			state(tuple(set(),set()): Tuple consisting of moves stored of each player.
			player (int): either 1 or 2 based on which players turn it is

		returns:
			optimal_a (list): list of optimal actions

	   """

		optimal_a = []
		self.a_v.clear()

		#player 1 maximizes utility value
		if player == 1:
			if(ab_prune):
				optimal_UV = self.max_ab(state, last_action = None, search_depth = 0)
			else:
				optimal_UV = self.max_(state, last_action = None, search_depth = 0)

		#player 2 minimizes utility
		elif player == 2: 
			if(ab_prune):
				optimal_UV = self.min_ab(state, last_action = None, search_depth = 0)
			else:
				optimal_UV = self.min_(state, last_action = None, search_depth = 0)

		if(ab_prune):
			for action, value in self.a_v.items():
				# Get non pruned actions.
				if value[0] == optimal_UV and not value[1]:
					optimal_a.append(action)
		else:
			for action, value in self.a_v.items():
				if value == optimal_UV:
					optimal_a.append(action)
		return optimal_a


	def play_game(self, ab_prune=False):
		"""

		The play function plays the entire game based on the user inputs.
		The user can either choose:

		1. Player vs Computer where the Player recieves 
		suggested moves based on minimax optimal action or 
		2. Computer vs Computer where the max and min actions are automatically chosen

		For Player vs Computer, the player is asked to enter the coordinates of where
		he/she wishes to place an X. There are checks to ensure that the players coordinates
		are on the board, or in an unoccupied cell. If the coordinates are invalid, the user
		is prompted to re-enter the values

		returns:
			time_list (list): a list of time taken for each move made by the computer.

		"""

		
		terminal = False
		winner = None

		times_list = [] #list of stored times for each move played

		#start the timer when the game begins
		game_start_time = time.time()

		player = 1 #start always with player 1
		
		while True:

			#draw the board
			state = self.state
			if self.display:
				self.drawboard(self.state)

			# if state reaches terminal state, then the game is over.
			if terminal:
				if winner == 1:
					print('Player 1 Wins!')
				elif winner == 2:
					print('You Lose! :(')
					print('Player 2 Wins!')
				elif winner == 0:
					print('Tie!')
				break

			print(f"Player {player}'s turn...")

			#human player
			if  player in self.human_players:

				#Make move recommendations to human player via minimax action
				
				actions = self.minimax_action(state, player, ab_prune=ab_prune)
				recommended_board_coordinates = self.array_coordinates_converter(actions)
				print('The computer recommends the following move(s):' + recommended_board_coordinates)


				board_coordinates = input('Input your move: ')
				while len(board_coordinates)<2:
					print(f'Sorry, the board coordinates {board_coordinates} are incorrect')
					print('The computer recommends the following move(s):' + recommended_board_coordinates)
					board_coordinates = input('Input your move: ')

				action = self.board_coordinates_converter(board_coordinates)

			# Computer player
			elif player in self.computer_player:
				#start the timer
				action_start_time = time.time()
				action = self.minimax_action(state, player, ab_prune=ab_prune)[0]
				action_end_time = time.time()
				#end the timer

				board_coordinates = self.array_coordinates_converter([action])
				times_list.append(action_end_time-action_start_time)
				print('The computer moves to: ' + board_coordinates)

			#check if the move is valid
			if self.is_valid(self.state, action):
				self.state = self.end_state(state, action, player)
				terminal, winner = self.is_terminal(self.state, action, player)
				#clear saved states to clear RAM space
				self.state_buffer.clear()

				#change player
				if player==2:
					player=1
				elif player==1:
					player=2

			else:

				print(f'Invalid move!. {board_coordinates} is either occupied or out of bounds.')

		game_end_time = time.time()
		times_list.append(game_end_time - game_start_time)
		return times_list,self.stored_states


	def find_value(self, state):
		"""
		Lookup the value for a stored state
		"""
		frozen_state = (frozenset(state[0]), frozenset(state[1]))
		if frozen_state in self.state_buffer:
			return(self.state_buffer[frozen_state])
		else:
			return None

	def clear(self):
		"""
		Clears all stored states
		"""
		self.state_buffer.clear()   



def main():
	"""
	Plays the game and calls the relevant functions.
	"""


	choice=int(input('Press 1 for Player vs Computer. Press 2 for Computer vs Computer  '))
	print(f'the choice is = {choice}')

	choice_ab=int(input('Do you want to play the game with Alpha beta Pruning. Press 1 for YES Press 2 for NO '))
	print(f'the choice is = {choice_ab}')

	choice_list=[]

	if choice==1:
		choice_list.append(int(1))
	elif choice==2:
		pass


	if choice_ab==1:
		game = Game(3, 3, 3, human_players =choice_list,computer_player = [1,2], display = True)
		time_list,states=game.play_game(True)
	elif choice_ab!=1:
		game = Game(3, 3, 3, human_players =choice_list,computer_player = [1,2], display = True)
		time_list,states=game.play_game(False)


	print(f'time to complete game = {time_list}')
	print(f'states visited = {states}')

def time_mnk(m, n, k):
	#game = Game(m, n, k, human_players =[],computer_player = [1,2], display = False)
	#times_noprune = game.play_game(False)
	game = Game(m, n, k, human_players =[],computer_player = [1,2], display = False)
	times_prune = game.play_game(True)
	times_noprune = []
	return times_noprune, times_prune

def times_test(m_max, n_max, k_max):
	times = np.zeros((m_max, n_max, k_max,2))
	for m in range(1,m_max+1):
		for n in range(1,n_max+1):
			for k in range(1,max(m, n, k_max+1)):
				times_noprune, times_prune = time_mnk(m, n, k)
				print(f"m = {m}, n = {n}, k = {k}:")
				print("No Pruning:")
				print(times_noprune)
				print("Pruning:")
				print(times_prune)
				#times[m-1,n-1,k-1,0] = np.array(times_noprune[-1])
				times[m-1,n-1,k-1,0] = np.array(times_prune[-1])
				#times[m-1,n-1,k-1,2] = np.mean(times_noprune[0][:-1])
				times[m-1,n-1,k-1,1] = np.mean(times_prune[0][:-1])
	return times

if __name__ == "__main__":
	main()
	# m_max = 4
	# n_max = 4
	# k_max = 4

	# results = times_test(m_max, n_max, k_max)
	# for k in range(0,k_max):
	# 	for m in range(0, m_max):
	# 		for n in range(0, n_max):
	# 			print(f"{(m+1,n+1,k+1)}: {results[m,n,k]}")

	

