"""
Acts as an interface for Markov State Determiners.

State Determiners may do whatever in the background, but must always have some "assign_state_to_vals" and
assign_state to data within them.
State Determiners should also have a clean_data_after_state assignment, which cleans the DF in the case where
moving values were used.
"""
class StateDeterminer():
    def __init__(self):
        # To be given by child class.
        self.possible_states = None
        self.ordered = None

    def assign_state_to_vals(self, *args, **kwargs):
        raise "Subclass should implement this method."

    def assign_state_to_data(self, *args, **kwargs):
        raise "Subclass should implement this method."

    def clean_data_after_state_assignment(self, *args, **kwargs):
        raise "Subclass should implement this method."

    def is_ordered(self):
        if self.ordered is None:
            raise "STATE DETERMINER SHOULD SPECIFY .ORDERED TO BE TRUE OR FALSE."
        return self.ordered

    def f(self):
        raise "Subclass should implement this method."