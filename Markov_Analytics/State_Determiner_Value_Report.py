from Driver.driver import assign_states_and_calculate_transition_probabilities, shorten_reports_and_write_json_pdfs
from Markov_Analytics.Analytics_Util import get_macro_units
from Markov_Analytics.Optimal_Quick_Calculation import get_max_1d_return_and_generate_dict_report
from Transition_Probability_Calculation.Empirical_Calculator import EmpiricalCalculator
import os

"""
Input: State Determiner, Scraper, Start & End Date.

Gives initial benchmarks on the value of a state space.

This should output:
1. MAX 1D Return (and all of its summary stats).
2. Plots of return distributions of each state (or col_in_question).
3. If state space is ordered, then:
    Output covariance with other data variables. HOWEVER! Hardcode mean of ordered state spaces to 

"""

def generate_value_report_from_scratch(ticker, state_determiner, scraper, start='2010-01-01', end='2024-01-01', transition_probability_calculator=None,
                                       test_against_random=False, N=100, col_to_optimize='daily_return', threshold=1,
                                       value_report_prefix='State_Determiner_Value_Reports', sd_name='placeholder'):
    print('Generating Value Report on State Space . . .')
    data = scraper.download_and_add_features(ticker)
    macro_units = get_macro_units(start, end)
    return generate_value_report_from_data(ticker, data, state_determiner, transition_probability_calculator=transition_probability_calculator,
                                           macro_units=macro_units, col_to_optimize=col_to_optimize, threshold=threshold,
                                           test_against_random=False, N=100,
                                           value_report_prefix=value_report_prefix, sd_name=sd_name)


def generate_value_report_from_data(ticker, data, state_determiner, transition_probability_calculator=None, macro_units=1,
                                    col_to_optimize='daily_return',threshold=1, test_against_random=False, N=100,
                                    value_report_prefix='State_Determiner_Value_Reports', sd_name='STATE_DET_NAME'):

    json_file=f'{sd_name}_value_raw'
    pdf_file=f'{sd_name}_graphs'
    json_file_prefix = pdf_file_prefix = f'{value_report_prefix}/{sd_name}/'

    if not os.path.exists(json_file_prefix):
        # Create directory
        os.makedirs(json_file_prefix)

    if not transition_probability_calculator:
        transition_probability_calculator = EmpiricalCalculator(state_determiner.possible_states)

    data, transition_probability_matrix = assign_states_and_calculate_transition_probabilities(data, state_determiner, transition_probability_calculator)

    oned_return_dict = get_max_1d_return_and_generate_dict_report(ticker, data, transition_probability_matrix, state_determiner,
                                         col_to_optimize=col_to_optimize, threshold =threshold,
                                                                  test_against_random=test_against_random, N=N)

    shorten_reports_and_write_json_pdfs([oned_return_dict], json_file=json_file, pdf_file=pdf_file,
                                        json_file_prefix=json_file_prefix,
                                        pdf_file_prefix=pdf_file_prefix, include_state_det_value_metrics=True, data=data)
    return data, oned_return_dict

