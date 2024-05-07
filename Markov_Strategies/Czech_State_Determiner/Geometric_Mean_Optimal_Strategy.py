from Markov_Strategies.Markov_Strategy import MarkovStrategy
class Geometric_Mean_Optimal_Strategy(MarkovStrategy):
    def invest_based_on_yesterday_state(self, prev_state, additional_bool=None):

        if prev_state in ['d2', 'g1', 'd3', 'g4', 'd4', 'd1']:
            return True
        return False