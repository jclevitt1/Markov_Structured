"""
Contour transition probabilty matrices are the same 1 dimensional case as normal transition probability matrices.
The only difference here is that contours go from a single state space to another. This means the (i, j)th element
of the contour transition probability matrix for state1_j, state2_i represents:

P(state2_i at time t | state1_j at time t - 1)

Exact same def as regular transition probability matrices, just across two different state spaces.

The single dimensional case is a subset of Contour space. We can make this abstraction later.
"""

class ContourTransitionProbabilityCalculator:
    def __init__(self, possible_states_before, possible_states_after):
        self.possible_states_before = possible_states_before
        self.possible_states_after = possible_states_after

    def calculate_transition_probabilities(self, *args, **kwargs):
        raise "Subclass should implement."