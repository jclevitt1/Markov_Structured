class TransitionProbabilityCalculator:
    def __init__(self, possible_states):
        self.possible_states = possible_states

    def calculate_transition_probabilities(self, *args, **kwargs):
        raise "Subclass should implement."