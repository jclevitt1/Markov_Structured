from Backtester.Markov_Backtester import MarkovBacktester
import numpy as np
from report_processor import shorten_reports, write_json_file, generate_pdf_report
"""
The main purpose of driver is to generate a report of a strategy based on historical backtest.

TODO: Better abstract the adjusted alpha functions. Leaving for now to just leave out best performing year.

NOTE- ALPHA is measured per macro unit time.
"""

def generate_report_files(tickers, scraper, state_determiner, transition_probability_calculator, markov_strategy,
                          start='2010-01-01', end='2024-01-01', test_against_random=False, N=100,
                          json_file='czech_strat1_raw', pdf_file='czech_strat1_graphs',
                          json_file_prefix='report_outputs/reports_jsons/',
                          pdf_file_prefix='report_outputs/report_graphs/', include_state_det_value_metrics=False):
    print('GENERATING REPORTS FROM SCRATCH, DATA NOT DOWNLOADED . . .')
    reports = compute_alpha_with_markov_strat_for_list_tickers(tickers, scraper, state_determiner, transition_probability_calculator,
                                                               markov_strategy, start=start, end=end,
                                                               test_against_random=test_against_random, N=N)
    shorten_reports_and_write_json_pdfs(reports, json_file=json_file, pdf_file=pdf_file,
                                        json_file_prefix=json_file_prefix, pdf_file_prefix=pdf_file_prefix,
                                        include_state_det_value_metrics=include_state_det_value_metrics)

def shorten_reports_and_write_json_pdfs(reports, json_file='czech_strat1_raw', pdf_file='czech_strat1_graphs',
                                        json_file_prefix='report_outputs/reports_jsons/',
                                        pdf_file_prefix='report_outputs/report_graphs/',
                                        include_state_det_value_metrics=False, data=None):
    shortened_reports = shorten_reports(reports)
    write_json_file(shortened_reports, json_file, file_prefix=json_file_prefix)
    generate_pdf_report(reports, pdf_file, file_prefix=pdf_file_prefix, include_state_det_value_metrics=include_state_det_value_metrics, data=data)
    # For now only using normal calculation of covariance. Will be replacing later on, but we want
    # An aggregate covariance matrix based on the state determiner used (since for now we only have Czech)
    # return_partial_cov_map(reports)

"""
Todo: move below function to appropriate class.
"""
def get_adjusted_alpha(m_over_bh_dts, m_p, macro_t_units, avg_bh_unit):
    val = max(m_over_bh_dts)
    ind = np.argmax(m_over_bh_dts)
    yrly_adj_markov = (m_p / val) ** (1 / macro_t_units)
    adj_alpha = yrly_adj_markov - avg_bh_unit
    return round(adj_alpha, 4), ind

def retrieve_data_and_add_features(ticker, scraper, start='2010-01-01', end='2024-01-01', L=20):
    print(f'Downloading and assigning states for {ticker}. . .')
    data = scraper.download_and_add_features(ticker, start=start, end=end, L=L)
    return data

def assign_states_and_calculate_transition_probabilities(data, state_determiner, transition_probability_calculator):
    print('Assigning states . . .')
    data = state_determiner.assign_state_to_data(data)
    print('Calculating transition probabilities . . .')
    transition_probability_matrix = transition_probability_calculator.calculate_transition_probabilities(data)
    return data, transition_probability_matrix
def retrieve_and_add_markov(ticker, scraper, state_determiner, transition_probability_calculator,
                            start='2010-01-01', end='2024-01-01'):
    data = retrieve_data_and_add_features(ticker, scraper, start=start, end=end)
    return assign_states_and_calculate_transition_probabilities(data, state_determiner, transition_probability_calculator)

def perform_backtest_on_strategy(ticker, state_derminer, data, markov_strategy,  transition_probability_matrix, test_against_random=True, N=100, possible_states=None):
    print('Beginning backtest . . .')
    markov_backtester = MarkovBacktester(data, markov_strategy)
    m_p, bh_p, markov_dts, bh_dts, m_over_bh_dts, total_days, macro_t_units, normal_cov_map, injected_state_0_cov_map, injected_state_return_0_cov_map  = markov_backtester.backtest_on_strategy(state_derminer)
    avg_m_unit, avg_bh_unit = m_p ** (1 / macro_t_units), bh_p ** (1 / macro_t_units)
    percentile = r_m = r_std = None
    if test_against_random:
        print(f'Testing against {N} simulations of random investment at the same frequency . . .')
        random_sim_results = markov_backtester.n_random_simulations(N)
        percentile = markov_backtester.get_percentile(random_sim_results, m_p)
        r_m, r_std = np.mean(random_sim_results), np.std(random_sim_results)
    # Also need percentile, and any adjusted alphas.
    print('Generating report . . .')
    return generate_full_dict_report(ticker, m_p, bh_p, avg_m_unit, avg_bh_unit, markov_dts, bh_dts, m_over_bh_dts, percentile, r_m, r_std, macro_t_units, transition_probability_matrix, possible_states, normal_cov_map, injected_state_0_cov_map, injected_state_return_0_cov_map)

def generate_full_dict_report(ticker, m_p, bh_p, avg_m_unit, avg_bh_unit, markov_dts, bh_dts, m_over_bh_dts, percentile, r_m, r_std, macro_t_units, transition_probability_matrix, possible_states, normal_cov_map, injected_state_0_cov_map, injected_state_return_0_cov_map):
    report = {}
    avg_alpha = avg_m_unit - avg_bh_unit
    alphas_by_dt = [markov_return_unit - bh_return_unit for markov_return_unit, bh_return_unit in zip(markov_dts, bh_dts)]
    adjusted_alpha, ind_removed = get_adjusted_alpha(m_over_bh_dts, m_p, macro_t_units, avg_bh_unit)
    report['Ticker'] = ticker
    report['Avg Alpha'] = avg_alpha
    report['Adj Alpha'] = adjusted_alpha
    report['M_P'] = m_p
    report['BH_P'] = bh_p
    report['Ind Removed'] = ind_removed
    report['Avg. Markov_R/MU_T'] = avg_m_unit
    report['Percentile (Against Random)'] = percentile
    report['Avg. BuyHold_R/MU_T'] = avg_bh_unit
    report['M/BH DTs'] = m_over_bh_dts
    report['markov_dts'] = markov_dts
    report['buy_hold_dts'] = bh_dts
    report['Random Mean'] = r_m
    report['Random Standard Deviation'] = r_std
    report['macro_t_units'] = macro_t_units
    report['Transition Probability Matrix'] = transition_probability_matrix
    report['Possible States'] = possible_states
    report['normal_cov_map'] = normal_cov_map
    report['type1_cov_map'] = injected_state_0_cov_map
    report['type2_cov_map'] = injected_state_return_0_cov_map
    print('Generated report!')
    return report

"""
Returns a report on historical backtest given a ticker, data scraper, state_determiner, transition probability calculator,
and markov strategy.
"""
def compute_alpha_with_markov_strat_for_ticker(ticker, scraper, state_determiner, transition_probability_calculator,
                                               markov_strategy, start='2010-01-01', end='2024-01-01',
                                               test_against_random=True, N=100):
    data, transition_probability_matrix = retrieve_and_add_markov(ticker, scraper, state_determiner,
                                                                  transition_probability_calculator,
                                                                  start=start, end=end,
                                                                  )
    return perform_backtest_on_strategy(ticker, state_determiner, data, markov_strategy, transition_probability_matrix, test_against_random=test_against_random, N=N, possible_states=state_determiner.possible_states)

"""
Returns a list of reports for the list of tickers given.
"""
def compute_alpha_with_markov_strat_for_list_tickers(tickers, scraper, state_determiner, transition_probability_calculator,
                                                     markov_strategy, start='2010-01-01', end='2024-01-01',
                                                     test_against_random=True, N=100):
    return [compute_alpha_with_markov_strat_for_ticker(ticker,  scraper, state_determiner, transition_probability_calculator,
                                                       markov_strategy, start=start, end=end,
                                                       test_against_random=test_against_random, N=N) for ticker in tickers]