from Driver.driver import perform_backtest_on_strategy
from Markov_Strategy_Determiner.Geometric_Mean_Probability_Optimizer import GeometricMeanProbabilityOptimizer
from Markov_State_Determiners.State_Determiner import StateDeterminer
from Markov_Strategies.Markov_Strategy import MarkovStrategy
from Backtester.Markov_Backtester import MarkovBacktester
from Markov_Strategy_Determiner.Markov_Strategy_Determiner import MarkovStrategyDeterminer

"""
A function that highly overfits data to observe the highest possible return for a given Markov state space, as a quick
check as to whether the state space is worth exploring.

HOWEVER!!! Do not be 1 dimensional in the way of thinking about this function. 

For now, this function can be a helpful way of knowing if there is potentially any causal (or highly correlated)
relations between a given state space and price. Later on though, it can provide more value than this.

Note how I have abstracted "COL_TO_OPTIMIZE." I think this will be VERY helpful later. While a state may not have
a direct causal relation on price, it may have a causal relation with another variable, which has its own relationship
with price.
"""
def get_max_1d_return_and_generate_dict_report(ticker, data, transition_probability_matrix, state_determiner: StateDeterminer,
                                               strategy_determiner: MarkovStrategyDeterminer = GeometricMeanProbabilityOptimizer,
                                          col_to_optimize='daily_return', threshold = 1, test_against_random=False, N=100):
    print(f'Generating MAX 1D return for {ticker}')
    possible_states_before = possible_states_after = state_determiner.possible_states
    sd = strategy_determiner(data, transition_probability_matrix,
                                                            possible_states_before, possible_states_after, col_to_optimize, threshold,
                                                            state_before_col='state', state_after_col='state')
    bet_dict = sd.determine_optimal_strategy()
    strategy = MarkovStrategy(bet_dict)
    return perform_backtest_on_strategy(ticker, state_determiner, data, strategy,  transition_probability_matrix,
                                 test_against_random=test_against_random, N=N, possible_states=state_determiner.possible_states)


def get_max_1d_return(data, transition_probability_matrix, state_determiner: StateDeterminer,
                      col_to_optimize='daily_return', threshold = 1, macro_units=1):
    # TODO: cache the process of downloading, state assignment, etc.
    possible_states_before = possible_states_after = state_determiner.possible_states
    czech_geo_optimizer = GeometricMeanProbabilityOptimizer(data, transition_probability_matrix,
                                                            possible_states_before, possible_states_after, col_to_optimize, threshold,
                                                            state_before_col='state', state_after_col='state')
    buy_conditions = czech_geo_optimizer.determine_optimal_strategy()
    strategy = MarkovStrategy(buy_conditions)
    backtester = MarkovBacktester(data, strategy)
    ret, bh_ret, m_dts, bh_dts, m_over_bh_dts, total_n, total_macro_units = backtester.backtest_on_strategy(state_determiner)
    d = {'ret': ret, 'avg_ret':(ret)**(1/macro_units), 'bh_ret':bh_ret, 'm_dts':m_dts, 'bh_dts': bh_dts,
         'm_over_bh_dts':m_over_bh_dts, 'total_n':total_n, 'total_macro_units': total_macro_units}
    return d