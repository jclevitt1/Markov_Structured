import pandas as pd
"""
1D case of Strategy Determiners.

Abstraction is as follows. Dev should call determine_optimal_strategy, which returns a list of buying conditions
which optimizes over the current strategy determiner.

How does this optimization occur? --> Score each prev_state, and have some threshold on this score that determines
whether buy should take place.

This is simple, but the scoring of each previous state can widely vary with the strategy determiner. Most naive idea
is to simply calculate the weighted average geo mean of each probability and expected return. This is GeometricMean
ProbabilityOptimizer. The scoring can also punish variance more, and punish outliers even more if desired.

---
Brainstorming possible MarkovStrategyDeterminers:
The idea of this scoring function is very basic like any in optimization function in stats:
Reward good things with positive values, punish bad things.

Good things in regard to buying conditions:
1. 

Bad things to punish
1. Variance
2. Outliers
3. Any sort of definition of risk that exists out there.
"""

class MarkovStrategyDeterminer:
    def __init__(self, data:pd.DataFrame, transition_probability_matrix,
                 possible_states_before, possible_states_after, col_to_optimize, threshold,
                state_before_col='state', state_after_col='state'):
        assert transition_probability_matrix.shape[0] == len(possible_states_after), "Length of possible states after should be equal to rows of transition probability matrix."
        assert transition_probability_matrix.shape[1] == len(possible_states_before), "Length of possible states before should be equal to columns of transition probability matrix."
        self.data = data
        self.transition_probability_matrix = transition_probability_matrix
        self.possible_states_before = possible_states_before
        self.possible_states_after = possible_states_after
        self.col_to_optimize = col_to_optimize
        self.threshold = threshold
        self.state_before_col = state_before_col
        self.state_after_col = state_after_col

    def determine_optimal_strategy(self):
        # Get geo mean of states.
        buying_conditions = {}
        for prev_state in self.possible_states_before:
            # Turn this into a list.
            bet_size, bool_bet = self.does_prev_state_meet_threshold(prev_state)
            if bool_bet:
                buying_conditions[prev_state] = bet_size
        return buying_conditions

    def does_prev_state_meet_threshold(self, prev_state, score_is_bet_size=False):
        score = self.score(prev_state)
        bet = 1*int(score >= self.threshold) if not score_is_bet_size else score
        if score >= self.threshold:
            return bet, True
        return bet, False

    def score(self, prev_state):
        raise "Subclass should implement."