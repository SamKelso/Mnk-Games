class Store_State_Values_Buffer:
    """
    The Store_State_Values_Buffer was created store state values. The purpose of this class
    is to improve execution time. Instead of searching the entire tree, the buffer stores previously visited states
    """


    def __init__(self):
        
        self.state_buffer = {}

    def add(self, state, value):
        """
        Adds a state to buffer.

		The frozenset() function returns an immutable frozenset object
		initialized with elements from the given iterable.

		A Frozen set is  an immutable version of a Python set object.
		While elements of a set can be modified at any time, elements of 
		the frozen set remain the same after creation.

        """
        frozen_state = (frozenset(state[0]), frozenset(state[1]))


        if frozenset not in self.state_buffer:
            self.state_buffer[frozen_state] = value
        else:
            pass

    def add_ab(self, state, value, pruned):
        """
        Adds a state to buffer.

		The frozenset() function returns an immutable frozenset object
		initialized with elements from the given iterable.

		A Frozen set is  an immutable version of a Python set object.
		While elements of a set can be modified at any time, elements of 
		the frozen set remain the same after creation.

        """
        frozen_state = (frozenset(state[0]), frozenset(state[1]))


        if frozenset not in self.state_buffer:
            self.state_buffer[frozen_state] = [value, pruned]
        else:
            pass

    def find_value(self, state):
        """
        Lookup the value for a stored state
        """
        frozen_state = (frozenset(state[0]), frozenset(state[1]))
        if frozen_state in self.state_buffer:
            return(self.state_buffer[frozen_state])
        else:
            return None

    def find_value_ab(self, state):
        """
        Lookup the value for a stored state
        """
        frozen_state = (frozenset(state[0]), frozenset(state[1]))
        if frozen_state in self.state_buffer:
            return(self.state_buffer[frozen_state])
        else:
            return None, False

    def clear(self):
        """
        Clears all stored states
        """
        self.state_buffer.clear()   

