import random

import pandas as pd

from Markov_Analytics.Analytics_Util import calculate_covariance_with_injection_option

"""
TODO: references to "days" as universal time unit should be renamed here. The logic is applicable to any granular unit
of time.
"""
class MarkovBacktester:
    def __init__(self, data, markov_strategy):
        self.data = data
        self.markov_strategy = markov_strategy
        self.p = 1
        self.total_days_invested = 0

    # Dividing_time_unit set to default 252 = market days per year.
    def backtest_on_strategy(self, state_determiner, DIVIDING_TIME_UNIT=252, places_to_round=5):
        data = self.data
        bh_p = 1 + (self.data.iloc[-1]['Adj Close'] - self.data.iloc[0]['Adj Close']) / (self.data.iloc[0]['Adj Close'])
        markov_strategy = self.markov_strategy
        bh_dts = []
        markov_dts = []
        m_over_bh_dts = []
        last_p = self.p
        for i in range(1, len(data)):
            prev_state = data.iloc[i - 1]['state']
            to_invest, s = markov_strategy.invest_based_on_yesterday_state(prev_state)
            if to_invest:
                self.total_days_invested += 1
                # This is wrong
                self.p *= (1 + s * data.iloc[i]['daily_return'])
            if i % DIVIDING_TIME_UNIT == 0 or i == len(data) - 1:
                index_prev = i - DIVIDING_TIME_UNIT
                bh_dt = 1 + (data.iloc[i]['Adj Close'] - data.iloc[index_prev]['Adj Close'] ) / data.iloc[index_prev]['Adj Close']
                markov_dt = self.p/last_p
                m_over_bh_dt = markov_dt / bh_dt
                bh_dts.append(round(bh_dt, places_to_round))
                markov_dts.append(round(markov_dt, places_to_round))
                m_over_bh_dts.append(round(m_over_bh_dt, places_to_round))
                last_p = self.p

        # Finally, generate covariances between markov states and col_in_question (in most cases daily_return)
        # We can also make this a list of cols later on easily.
        # This need not be in the backtest function, but for now this is not a large barrier, so leaving here for ease.
        normal_cov_map = None
        injected_state_0_cov_map = None
        injected_state_return_0_cov_map = None

        if state_determiner is not None and state_determiner.is_ordered():
            normal_cov_map = {}
            injected_state_0_cov_map = {}
            injected_state_return_0_cov_map = {}
            nominal_state_col_name = 'state_nominal'
            for column in data.columns:
                if column == 'state':
                    pass
                else:
                    # Putting the below as single element lists so DF does not complain.
                    normal_cov_map[column] = [calculate_covariance_with_injection_option(data[column], data[nominal_state_col_name])]
                    injected_state_0_cov_map[column] = [calculate_covariance_with_injection_option(data[column], data[nominal_state_col_name], injected_mean_b=0)]
                    injected_state_return_0_cov_map[column] = [calculate_covariance_with_injection_option(data[column], data[nominal_state_col_name], injected_mean_a=0, injected_mean_b=0)]
            normal_cov_map = pd.DataFrame(normal_cov_map)
            injected_state_0_cov_map = pd.DataFrame(injected_state_0_cov_map)
            injected_state_return_0_cov_map = pd.DataFrame(injected_state_return_0_cov_map)

        return round(self.p, 5), round(bh_p, 5), markov_dts, bh_dts, m_over_bh_dts, self.total_days_invested, round(len(data) / DIVIDING_TIME_UNIT, 1), normal_cov_map, injected_state_0_cov_map, injected_state_return_0_cov_map

    def random_investment_given_days(self):
        data = self.data
        prob = self.total_days_invested / len(data)
        p = 1
        for i in range(len(data)):
            invest = random.random() < prob # choose random boolean based on prob
            if invest:
                p *= 1 + data.iloc[i]['daily_return']
        return p

    def n_random_simulations(self, n):
        random_day_investments = []
        for i in range(n):
            random_day_investments.append(self.random_investment_given_days())
        random_day_investments = sorted(random_day_investments)
        return random_day_investments

    def get_percentile(self, sorted_list, p):
        for i in range(len(sorted_list)):
            if p < sorted_list[i]:
                return (i / len(sorted_list)) * 100
        return 100