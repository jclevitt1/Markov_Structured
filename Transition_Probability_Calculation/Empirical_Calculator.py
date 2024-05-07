from Transition_Probability_Calculation.Transition_Probability_Calculator import TransitionProbabilityCalculator
import pandas as pd

class EmpiricalCalculator(TransitionProbabilityCalculator):
    def __init__(self, possible_states, state_col='state'):
        self.state_col = state_col
        super().__init__(possible_states)

    def calculate_transition_probabilities(self, data, num_states=8):
        N = len(data)
        # The following dictionary structure allows us to keep track of numerators simply by indexing as follows
        # transition_probs[last_state][curr_state] = numerator.
        transition_probs = {state: {} for state in self.possible_states}
        denoms_for_probs = {state: 0 for state in self.possible_states}
        for before_state in self.possible_states:
            for after_state in self.possible_states:
                transition_probs[before_state][after_state] = 0
        for i in range(1, len(data)):
            last_state = data.iloc[i - 1][self.state_col]
            curr_state = data.iloc[i][self.state_col]
            transition_probs[last_state][curr_state] += 1
            denoms_for_probs[last_state] += 1

        for before_state in self.possible_states:
            for after_state in self.possible_states:
                if denoms_for_probs[before_state] != 0:
                    transition_probs[before_state][after_state] = transition_probs[before_state][after_state] / denoms_for_probs[before_state]
                else:
                    transition_probs[before_state][after_state] = 0
        return pd.DataFrame(transition_probs)
