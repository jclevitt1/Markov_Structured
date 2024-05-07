from Transition_Probability_Calculation.Contour_Transition_Probability_Calculator import ContourTransitionProbabilityCalculator
import pandas as pd

class ContourEmpiricalCalculator(ContourTransitionProbabilityCalculator):
    def __init__(self, possible_states_before, possible_states_after, state_before_col='state', state_after_col='state2'):
        self.state_before_col = state_before_col
        self.state_after_col = state_after_col
        super().__init__(possible_states_before, possible_states_after)

    def calculate_transition_probabilities(self, data):
        # The following dictionary structure allows us to keep track of numerators simply by indexing as follows
        # transition_probs[last_state][curr_state] = numerator.
        transition_probs = {state: {} for state in self.possible_states_before}
        denoms_for_probs = {state: 0 for state in self.possible_states_before}
        for before_state in self.possible_states_before:
            for after_state in self.possible_states_after:
                transition_probs[before_state][after_state] = 0
        for i in range(1, len(data)):
            last_state = data.iloc[i - 1][self.state_before_col]
            curr_state = data.iloc[i][self.state_after_col]
            transition_probs[last_state][curr_state] += 1
            denoms_for_probs[last_state] += 1

        for before_state in self.possible_states_before:
            for after_state in self.possible_states_after:
                if denoms_for_probs[before_state] != 0:
                    transition_probs[before_state][after_state] = transition_probs[before_state][after_state] / denoms_for_probs[before_state]
                else:
                    transition_probs[before_state][after_state] = 0
        trans_prob_matrix = pd.DataFrame(transition_probs)
        trans_prob_matrix = trans_prob_matrix.sort_index(axis=0).sort_index(axis=1)
        return trans_prob_matrix
