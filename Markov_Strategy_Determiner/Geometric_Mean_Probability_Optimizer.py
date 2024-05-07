from Markov_Strategy_Determiner.Markov_Strategy_Determiner import MarkovStrategyDeterminer
from Markov_Analytics.Analytics_Util import get_geo_mean_of_state, calculate_weighted_geo_mean, calculate_after_state_geo_means_given_prev_state
import pandas as pd

"""
A Markov Strategy Determiner that optimizes as follows:


"""
class GeometricMeanProbabilityOptimizer(MarkovStrategyDeterminer):
    def __init__(self, data:pd.DataFrame, transition_probability_matrix,
                 possible_states_before, possible_states_after, col_to_optimize, threshold,
                 state_before_col='state', state_after_col='state'):
        super().__init__(data, transition_probability_matrix,
                         possible_states_before, possible_states_after, col_to_optimize, threshold,
                         state_before_col=state_before_col, state_after_col=state_after_col)
        # self.after_state_geo_means = self.calculate_all_geo_means()


    """
    Only should be used in average state.
    """
    def calculate_all_geo_means(self):
        after_states_geo_means = {}
        for after_state in self.possible_states_after:
            after_states_geo_means[after_state] = get_geo_mean_of_state(self.data, after_state, state_col=self.state_after_col, col_to_mean=self.col_to_optimize)
        return after_states_geo_means


    def score(self, prev_state):
        probabilities = self.transition_probability_matrix[prev_state]
        after_state_geo_means = calculate_after_state_geo_means_given_prev_state(self.data, prev_state, prev_state_col='state',
                                                                                 possible_states_after=self.possible_states_after, after_state_col='state',
                                                                                 col_in_q='daily_return')
        weighted_geo = calculate_weighted_geo_mean(probabilities, after_state_geo_means, self.possible_states_after)
        return weighted_geo



