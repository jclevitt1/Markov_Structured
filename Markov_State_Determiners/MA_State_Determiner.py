"""
This is the first Markov state determiner I ever made.

It is based on the paper https://dspace5.zcu.cz/bitstream/11025/46493/1/EM_4_2021_09.pdf .

Let's look into assigning similar czech states across different columns. I.e. EMA vs. price instead of EMA vs EMA.
"""
from Markov_State_Determiners.State_Determiner import StateDeterminer
import pandas as pd

class MAStateDeterminer(StateDeterminer):
    g1 = 'g1'
    g2 = 'g2'
    g3 = 'g3'
    g4 = 'g4'
    d1 = 'd1'
    d2 = 'd2'
    d3 = 'd3'
    d4 = 'd4'

    def possible_states(self):
        return set([g1, g2, g3, g4, d1, d2, d3, d4])

    def __init__(self, k, l, ma_col, price_col, state_col='state', nominal_state_col='state_nominal',
                 injected_mean_function = None
                 ):
        self.k = k
        self.l = l
        self.ma_col = ma_col
        self.price_col = price_col
        self.state_col = state_col
        self.nominal_state_col = nominal_state_col
        self.ordered = True
        self.possible_states = set(['g1', 'g2', 'g3', 'g4', 'd1', 'd2', 'd3', 'd4'])
        # If no function is passed in for injected_mean function, we assume we are taking daily_return as col,
        # which we should have an injected mean of 0 by default.
        if not injected_mean_function:
            injected_mean_function = lambda data, col: pd.Series([0 for i in range(len(data))])
        self.injected_mean_function = injected_mean_function


    def assign_state_to_vals(self, val, std, ma=0):
        if ma <= val < ma + std * self.k:
            return 'g1'
        elif ma + std * self.k <= val < ma + 2 * std * self.k:
            return 'g2'
        elif ma + 2 * std * self.k <= ma + val < 3 * std * self.k:
            return 'g3'
        elif ma + 3 * std * self.k <= ma + val:
            return 'g4'
        elif ma -1 * std * self.k <= val < ma:
            return 'd1'
        elif ma -2 * std * self.k <= val < ma -1 * std * self.k:
            return 'd2'
        elif ma -3 * std * self.k <= val < ma -2 * std * self.k:
            return 'd3'
        else:
            return 'd4'

    def clean_data_after_state_assignment(self, data):
        data = data[self.l:]
        # print(data[-20:].head(15))
        # data = data.dropna()
        return data

    def add_in_l_day_sd(self, data):
        name = 'STD_L=' + str(self.l)
        if name in data.columns:
            return data, name
        data[name] = data[self.col_to_std].rolling(window=self.l).std()
        return data, name

    # Injected mean function is the
    def assign_state_to_data(self, data):
        data, std_name = self.add_in_l_day_sd(data)
        state_arr = [None for i in range(self.l)]
        nominal_state_arr = [None for i in range(self.l)]
        ma_series = data[self.ma_col]
        for i in range(self.l, len(data)):
            std = data.iloc[i][std_name]
            state = self.assign_state_to_vals(data.iloc[i][self.price_col], std, ma=ma_series.iloc[i])
            state_arr.append(state)
            nominal_state_arr.append(self.f(state))
        data[self.state_col] = state_arr
        data[self.nominal_state_col] = nominal_state_arr
        data = self.clean_data_after_state_assignment(data)
        return data

    """
    Replace later on with some exponential weighted f.
    """
    def f(self, state):
        if state[0] == 'g':
            return int(state[1]) * 0.25
        return -int(state[1]) * 0.25