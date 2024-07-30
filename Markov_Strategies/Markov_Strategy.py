"""
Flushing out some thoughts on Markov chains- whether or not to vary both state defintions and transition probabilities
per unit time.

The definition I will be using for a PURE Markov Strategy is one which only invests based on previous state.

That is, given a previous state, invest if state is a constant. This can be integrated with other decision making
models with a simple addition of an additional boolean. For simplicity and atomicity, it is best to make Markov model
in this fashion.

The math-ey theory behind why only previous state should be factored into decision making is the same reasoning for which
transition probabilities must be a constant throughout a Markov chain . . .

Varying both state definitions with unit time AS WELL AS transition probabilities muddies the waters and states begin
to lose their definite meaning. What information does knowing "x will transition to y with probability 100%" if the
definition of y changes at the next dt increase?? ANSWER: if the definition changes negligibly, then not much info is
lost. However, as model scales up to more granular units of time, it does not make sense to do so as information is
lost much quicker as unit time shrinks while state definitions and transition probabilities continue to vary with each
passing unit.
"""

class MarkovStrategy():
    """
    Additional bool allows for strategy to be conjoined with additional strategy. The other strategy only needs to
    output decision of TRUE or FALSE to buy/not, given by additional bool. For all cases now, this is None.
    """
    def __init__(self, bet_dict):
        self.bet_dict = bet_dict
    def invest_based_on_yesterday_state(self, prev_state, additional_bool=None):
        if prev_state in self.bet_dict:
            return True, self.bet_dict[prev_state]
        return False, 0