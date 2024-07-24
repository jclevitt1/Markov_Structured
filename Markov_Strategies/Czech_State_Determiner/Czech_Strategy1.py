from Markov_Strategies.Markov_Strategy import MarkovStrategy
class CzechStrategy1(MarkovStrategy):
    def __init__(self):
        self.bets = {'g1': 7.89580801,
                     'g2': 3.31633209,
                     'g3': -7.90178457,
                     'g4': -1.3914714,
                     'd1': 7.27949125,
                     'd2': 2.94271177,
                     'd3': 10.13161884,
                     'd4': 9.20576061}
    def invest_based_on_yesterday_state(self, prev_state, additional_bool=None, constrain=False):
        if constrain:
            return True, self.constrain_bet(prev_state)
        return True, self.bets[prev_state]

    def constrain_bet(self, prev_state, method='max_magnitude', MAX_LEVERAGE=1):
        if method == 'max_magnitude':
            pos = [i for i in self.bets.values() if i >= 0]
            neg = [abs(y) for y in self.bets.values() if y < 0]
            if self.bets[prev_state] >= 0:
                return self.bets[prev_state] / max(pos)
            return self.bets[prev_state] / max(neg)
        # Nice

        if abs(self.bets[prev_state]) > MAX_LEVERAGE:
            return MAX_LEVERAGE


