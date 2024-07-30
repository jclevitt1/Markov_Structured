from Kelly_Box.Kelly_Box import get_optimal_bet_next_unit, fit_kde_functions
from Markov_Strategy_Determiner.Markov_Strategy_Determiner import MarkovStrategyDeterminer
from Markov_Analytics.Analytics_Util import get_geo_mean_of_state, calculate_weighted_geo_mean, calculate_after_state_geo_means_given_prev_state
import pandas as pd

"""
A Markov Strategy Determiner that uses the Kelly criterion 


"""
class KellyStrategyDeterminer(MarkovStrategyDeterminer):
    def __init__(self, data:pd.DataFrame, transition_probability_matrix,
                 possible_states_before, possible_states_after, col_to_optimize, threshold,
                 state_before_col='state', state_after_col='state', MAX_LEVERAGE=10):
        super().__init__(data, transition_probability_matrix,
                         possible_states_before, possible_states_after, col_to_optimize, threshold,
                         state_before_col=state_before_col, state_after_col=state_after_col)
        filtered_data = self.filter_data_by_state()
        state_kde_functions = fit_kde_functions(filtered_data)
        # The weights are given by the transition probability matrix in this case.
        return_pdf_by_prev_state = { s: self.t_plus_1_distribution(state_kde_functions, self.transition_probability_matrix,
                                                                   s, possible_states=self.possible_states_before) for s in self.possible_states_before}
        optimal_bet_solution_by_prev_state = { s: get_optimal_bet_next_unit(return_pdf_by_prev_state[s]) for s in self.possible_states_before}
        self.optimal_bet_unit_by_prev_state = { s: optimal_bet_solution_by_prev_state[s].x for s in self.possible_states_before}
        for state in self.possible_states_before:
            if self.optimal_bet_unit_by_prev_state[state] > MAX_LEVERAGE:
                self.optimal_bet_unit_by_prev_state[state] = int(self.optimal_bet_unit_by_prev_state[state] > 0) * MAX_LEVERAGE
                # self.after_state_geo_means = self.calculate_all_geo_means()

    def determine_optimal_strategy(self):
        return self.optimal_bet_unit_by_prev_state

    def t_plus_1_distribution(self, distributions_by_state, tpm, prev_state, possible_states):
        def return_pdf(x):
            pdf_val = 0
            for next_state in possible_states:
                if distributions_by_state[next_state] is not None:
                    pdf_val += tpm[prev_state][next_state] * distributions_by_state[next_state](x)
            return pdf_val
        return return_pdf

    # TODO: Move this out of this function later.
    def filter_data_by_state(self):
        data = self.data
        filtered_data = {}
        for possible_state in data['state'].unique():
            filtered_data[possible_state] = data[data['state'] == possible_state]
        return filtered_data
