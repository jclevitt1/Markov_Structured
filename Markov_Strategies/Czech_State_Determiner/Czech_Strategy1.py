from Markov_Strategies.Markov_Strategy import MarkovStrategy
class CzechStrategy1(MarkovStrategy):
    def __init__(self):
        pass
    def invest_based_on_yesterday_state(self, prev_state, additional_bool=None):
        if prev_state == 'd3' or prev_state == 'g1' or prev_state == 'd1' or prev_state == 'd2':
            return True, 1
        return False, 0