import numpy as np
import json
import pandas as pd
from report_processor import write_json_file
import matplotlib.pyplot as plt
from report_processor import save_all_figures_to_single_pdf

# TODO: think about how to integrate

def get_number_combos(record):
    return len(record)

def get_num_instances_given_state(record, state):
    return len(record[state])

def get_percent_over_bound_given_state(record, record_over_b, state):
    over_b = record_over_b[state][0]
    total_occurences = get_num_instances_given_state(record, state)
    return round(100 * over_b / total_occurences, 2)

def get_percent_profitable_given_state(returns):
    num_profitable = sum([1 if val > 0 else 0 for val in returns])
    return round(100 * num_profitable / len(returns), 1)

"""
Summary stats to collect:

1.
"""
def collect_summary_stats_given_state(record, records_over_b, state, col_in_question='daily_return'):
    returns = [dict[col_in_question] for dict in record[state]]
    avg_r = calculate_geo_mean([1 + r for r in returns]) - 1
    avg_return = round(100 * avg_r, 2)
    percent_profitable = get_percent_profitable_given_state(returns)
    percent_over_b = get_percent_over_bound_given_state(record, records_over_b, state)
    std = np.std(returns)
    num_instances = get_num_instances_given_state(record, state)
    return returns, avg_return, percent_profitable, percent_over_b, std, num_instances


# TODO: Move this to a more appropriate file.
def calculate_geo_mean(vals):
    p = 1
    for val in vals:
        p *= val
    return p ** (1 / len(vals))

def generate_report_list(records, records_over_b, col_in_question='daily_return', instance_threshhold=4):
    report_list = []
    for state in records.keys():
        curr_dict = {}
        curr_dict['State Combo'] = state
        returns, avg_return, percent_profitable, percent_over_b, std, num_instances = collect_summary_stats_given_state(records, records_over_b, state, col_in_question=col_in_question)
        if num_instances > instance_threshhold:
            curr_dict['Num Instances'] = num_instances
            curr_dict['Avg Return %'] = avg_return
            curr_dict['Profitable %'] = percent_profitable
            curr_dict['Over B %'] = percent_over_b
            curr_dict['STD'] = std
            curr_dict['Returns'] = returns
            report_list.append(curr_dict)
    report_list = sorted(report_list, key = lambda x: (-x['Avg Return %'], -x['Num Instances']))
    return report_list

"""
This function outputs a report on the negative and positive significant states.
"""
def collect_summary_on_combos(positive_records, negative_records, positive_records_over_b, negative_records_over_b, instance_threshhold=4):
    reports = {}
    reports['Positive SigStates Count'] = get_number_combos(positive_records)
    reports['Negative SigStates Count'] = get_number_combos(negative_records)
    reports['positive_reports'] = generate_report_list(positive_records, positive_records_over_b, instance_threshhold=instance_threshhold)
    reports['negative_reports'] = generate_report_list(negative_records, negative_records_over_b, instance_threshhold=instance_threshhold)
    return reports

def make_json_report_from_scratch(file_name, positive_records, negative_records, positive_records_over_b, negative_records_over_b,
                     markov1_name='markov_1', markov2_name='markov_2'):
    reports = collect_summary_on_combos(positive_records, negative_records, positive_records_over_b, negative_records_over_b)
    write_json_file(reports, file_name=file_name, file_prefix=f'Intersecting_Model_Analytic_Outputs/{markov1_name}.{markov2_name}/')

def make_json_report_from_dict(reports, markov1_name='markov_1', markov2_name='markov_2'):
    write_json_file(reports, file_name='raw_reports', file_prefix=f'Intersecting_Model_Analytic_Outputs/{markov1_name}.{markov2_name}/')


def generate_return_hist(report, markov1_name='', markov2_name=''):
    state_combo = report['State Combo']
    returns = [r * 100 for r in report['Returns']]
    num_instances = report['Num Instances']
    fig = plt.figure(figsize=(4, 4))
    plt.title(f'Returns for {state_combo} : {markov1_name}.{markov2_name}')
    plt.hist(returns)
    plt.text(x=0.6, y=0.94, s=f'Num instances: {num_instances}', color='black', transform=plt.gca().transAxes, fontsize=8)
    plt.close()
    return fig

def generate_date_hist(report, records_over_b, markov1_name='', markov2_name=''):
    state_combo = report['State Combo']
    fig = plt.figure(figsize=(4, 4))
    plt.title(f'Dates for Over B for {state_combo} : {markov1_name}.{markov2_name}')
    over_b = records_over_b[state_combo][0]
    year_list = [ts.year for ts in records_over_b[state_combo][1]]
    plt.hist(year_list)
    plt.text(x=0.75, y=0.94, s=f'Over B: {over_b}', color='black', transform=plt.gca().transAxes, fontsize=8)
    plt.close()
    return fig

# In contrast with reports when a strategy is known, these reports only apply for a single security, and
# reflect reports on the significant state combinations as defined.
def save_intersecting_graphs_to_pdf(report_list, records_over_b, markov1_name='', markov2_name='', positive=True):
    figures = []
    for i in range(len(report_list)):
        report = report_list[i]
        figures.append(generate_return_hist(report, markov1_name=markov1_name, markov2_name=markov2_name))
        figures.append(generate_date_hist(report, records_over_b, markov1_name=markov1_name, markov2_name=markov2_name))
    file_prefix = f'Intersecting_Model_Analytic_Outputs/{markov1_name}.{markov2_name}/'
    if positive:
        file_n = 'positive_combos'
    else:
        file_n = 'negative_combos'
    save_all_figures_to_single_pdf(figures, file_n, file_prefix=file_prefix)

def save_transition_prob_matrix_as_csv(trans_prob: pd.DataFrame, is_markov1: bool, markov1_name='', markov2_name='', file_name=None):
    m = markov1_name if is_markov1 else markov2_name
    if not file_name:
        print(f'Saving Transition Probability matrices for {m}')
        file_name = f'Intersecting_Model_Analytic_Outputs/{markov1_name}.{markov2_name}/{m}_trans_prob_matrix.csv'
    else:
        print(f'Saving Contour Transition Probabilities {file_name}')
        file_name = f'Intersecting_Model_Analytic_Outputs/{markov1_name}.{markov2_name}/{file_name}.csv'
    trans_prob.to_csv(file_name)
    print('Saved.')

def generate_summary_df(reports):
    df = {}
    state_combos, num_instances, avg_return, profitable, over_b, std = [], [], [], [], [], [],
    for report in reports:
        state_combos.append(report['State Combo'])
        num_instances.append(report['Num Instances'])
        avg_return.append(report['Avg Return %'])
        profitable.append(report['Profitable %'])
        over_b.append(report['Over B %'])
        std.append(report['STD'])
    df['State Combo'] = state_combos
    df['Num Instances'] = num_instances
    df['Avg Return %'] = avg_return
    df['Profitable %'] = profitable
    df['Over B %'] = over_b
    df['STD'] = std
    return pd.DataFrame(reports)

def save_summary_df(reports, markov1_name='', markov2_name=''):
    print('Saving summary DFs for negative and positive significant combos.')
    file_prefix = f'Intersecting_Model_Analytic_Outputs/{markov1_name}.{markov2_name}/'
    positive_reports = reports['positive_reports']
    negative_reports = reports['negative_reports']
    generate_summary_df(positive_reports).to_csv(f'{file_prefix}positive_reports.csv')
    generate_summary_df(negative_reports).to_csv(f'{file_prefix}negative_reports.csv')
    print('Saved.')

def save_summary_to_files(markov1_transition_prob_matrix, markov2_transition_prob_matrix, m1_m2_contour, m2_m1_contour,
                          positive_records, negative_records, positive_records_over_b, negative_records_over_b,
                          markov1_name='markov_1', markov2_name='markov_2', instance_threshhold=4):

    reports = collect_summary_on_combos(positive_records, negative_records, positive_records_over_b, negative_records_over_b, instance_threshhold=instance_threshhold)
    make_json_report_from_dict(reports, markov1_name=markov1_name, markov2_name=markov2_name)
    save_summary_df(reports, markov1_name=markov1_name, markov2_name=markov2_name)
    save_transition_prob_matrix_as_csv(markov1_transition_prob_matrix, is_markov1=True, markov1_name=markov1_name, markov2_name=markov2_name)
    save_transition_prob_matrix_as_csv(m1_m2_contour, is_markov1=False, markov1_name=markov1_name, markov2_name=markov2_name, file_name=f'{markov1_name}.{markov2_name}_contour')
    save_transition_prob_matrix_as_csv(m2_m1_contour, is_markov1=True, markov1_name=markov1_name, markov2_name=markov2_name, file_name=f'{markov2_name}.{markov1_name}_contour')
    save_transition_prob_matrix_as_csv(markov2_transition_prob_matrix, is_markov1=False, markov1_name=markov1_name, markov2_name=markov2_name)
    #Need to save
    save_intersecting_graphs_to_pdf(reports['positive_reports'], positive_records_over_b, markov1_name=markov1_name, markov2_name=markov2_name, positive=True)
    save_intersecting_graphs_to_pdf(reports['negative_reports'], negative_records_over_b, markov1_name=markov1_name, markov2_name=markov2_name, positive=False)