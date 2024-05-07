import numpy as np
from collections import defaultdict
def get_geo_mean_of_state(data, state, state_col='state', col_to_mean='daily_return'):
    filtered_returns = data[data[state_col]==state][col_to_mean]
    geo_mean = 0
    for i in range(len(filtered_returns)):
        geo_mean += np.log(1 + filtered_returns.iloc[i])
    geo_mean = np.exp(geo_mean / len(filtered_returns)) if len(filtered_returns) >= 1 else 1
    return geo_mean

def calculate_weighted_geo_mean(probabilities, expected_returns, possible_states):
    weighted_geo_mean = 1
    for state in possible_states:
        weighted_geo_mean *= expected_returns[state] ** (probabilities[state])
    return weighted_geo_mean

def calculate_after_state_geo_means_given_prev_state(data, prev_state, prev_state_col, possible_states_after, after_state_col, col_in_q='daily_return'):
    n = 0
    after_state_means = defaultdict(lambda: 1)
    after_state_ns = defaultdict(lambda: 0)
    for i in range(1, len(data)):
        if data.iloc[i - 1][prev_state_col] == prev_state:
            after_state = data.iloc[i][after_state_col]
            after_state_means[after_state] *= (1 + data.iloc[i][col_in_q])
            after_state_ns[after_state] += 1
    for state in possible_states_after:
        after_state_means[state] = after_state_means[state] ** (1 / after_state_ns[state]) if after_state_ns[state] else 1
    return after_state_means

def get_prs_and_exp_returns(data, prev_state, possible_states, trans_prob_matrix):
    expected_prob = []
    expected_returns = []
    expected_returns_constant = {state: get_geo_mean_of_state(data, state) for state in possible_states}
    for state in possible_states:
        expected_prob.append(trans_prob_matrix[prev_state][state])
        expected_returns.append(expected_returns_constant[state])
    return expected_prob, expected_returns

"""
For now, MACRO UNITS is years. Later on this will change. this function is a little hardcoded to the amount of years
given.
"""
def get_macro_units(start, end):
    return int(end[:4]) - int(start[:4])

"""
Fully abstracted covariance function. Cov is defined as
sum [ (x_i - x_bar) (y_i - y_bar) ] /n

abstracted so one can inject x_bar, y_bar, and determine distance function (as opposed to ordinary subtraction).

"""
def calculate_covariance_with_injection_option(list_a, list_b, injected_mean_a=None, injected_mean_b=None, distance_a=None, distance_b=None):
    if injected_mean_a is None:
        injected_mean_a = np.mean(list_a)
    if injected_mean_b is None:
        injected_mean_b = np.mean(list_b)
    if distance_a is None:
        distance_a = lambda x: x - injected_mean_a
    if distance_b is None:
        distance_b = lambda x: x - injected_mean_b
    sd_injected_a = determine_sd_injected(list_a, distance_a)
    sd_injected_b = determine_sd_injected(list_b, distance_b)
    normalization_factor = sd_injected_a * sd_injected_b
    cov = 0
    for a, b in zip(list_a, list_b):
        cov += distance_a(a) * distance_b(b)
    cov = cov / (len(list_a) * normalization_factor)
    return cov

"""
Even though the squaring may not seem abstract, this is correct, as is in line with the covariance abstraction above
since dim includes mult two datapoints at once (just with separate distance functions).
"""
def determine_sd_injected(l, distance_f):
    sd = 0
    for val in l:
        sd += distance_f(val) ** 2
    return (sd / len(l)) ** (1 / 2)


def output_significant_cov(df, threshold=0.65):
    toReturn = []
    for col in df.columns:
        for index, value in df[col].items():
            abs_value = abs(value)
            if col == 'state_nominal' or col == index:
                pass
            elif abs_value > threshold:
                # Append the ((index, column), value) if condition is met
                toReturn.append([(index, col), value])
    return toReturn