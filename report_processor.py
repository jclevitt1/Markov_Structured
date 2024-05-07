import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os

"""
This script defines a list of functions to be used on a list of reports as outputted by the driver of the program.
"""

def avg_param(reports, param):
    toReturn = 0
    for report in reports:
        toReturn += report[param]
    return round(toReturn / len(reports), 4)

# def std_param(reports, param):


def avg_delta_params(reports, param1, param2):
    toReturn = 0
    for report in reports:
        toReturn += report[param1] - report[param2]
    return round(toReturn / len(reports), 4)

def shorten_reports(reports, keys_to_remove=['M/BH DTs', 'markov_dts', 'buy_hold_dts', 'Transition Probability Matrix',
                                             'Possible States', 'normal_cov_map', 'type1_cov_map','type2_cov_map']):
    copy_reports = []
    for report in reports:
        copy_report = report.copy()
        for key in keys_to_remove:
            del copy_report[key]
        copy_reports.append(copy_report)
    return copy_reports

def generate_figs(reports, include_state_det_value_metrics=False, data=None):
    figs = []
    for report in reports:
        figs.append(generate_return_graph(report))
        figs.append(generate_alpha_graph(report))
        figs.append(save_transition_probabilities_to_pdf(report))
        if include_state_det_value_metrics:
            for state in sorted(report['Possible States']):
                figs.append(generate_return_vs_state_graph(data, state))
            cov_maps_to_include = ['normal_cov_map', 'type1_cov_map', 'type2_cov_map']
            cov_maps_to_include = ['normal_cov_map']
            for cov_map in cov_maps_to_include:
                curr_df = generate_covariance_table(cov_map, report)
    return figs # save_all_figures_to_single_pdf(figs, filename=filename)

def generate_covariance_table(cov_map_type, report, fontsize=25):
    df = report[cov_map_type]
    df = df.sort_index(axis=0).sort_index(axis=1)
    df = round(df * 100, 1)
    fig, ax =plt.subplots(figsize=(12,4))
    ticker = report['Ticker']
    plt.title(f'{ticker} {cov_map_type}')
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values,colLabels=df.columns,rowLabels=df.index,loc='center')
    table_props = the_table.properties()
    table_cells = table_props['children']
    for cell in table_cells:
        cell.set_fontsize(fontsize)  # Adjust font size here
    plt.close(fig)
    return fig


def generate_return_vs_state_graph(data, state, col_in_q='daily_return'):
    if data is None:
        raise "data should not be none for generating return vs state histograms."
    fig = plt.figure(figsize=(4, 4))
    total_data_len = len(data)
    values_in_q = get_values_in_q(data, state, col_in_q=col_in_q)
    plt.title(f'State Return Distribution for State {state}')
    count, bins, _ = plt.hist(values_in_q, bins=15, density=True, edgecolor='black')
    n = len(values_in_q)
    bin_size = round(bins[1] - bins[0], 3)
    plt.xlabel('Percent Return (or col_in_q)')
    plt.ylabel('Relative Frequency')
    plt.text(x=0.65, y=0.94, s=f'Bin Size: {bin_size}', color='black', transform=plt.gca().transAxes, fontsize=8)
    plt.text(x=0.65, y=0.89, s=f'Num Instances {state}: {n}', color='black', transform=plt.gca().transAxes, fontsize=8)
    plt.text(x=0.65, y=0.84, s=f'Total Data Len: {total_data_len}', color='black', transform=plt.gca().transAxes, fontsize=8)
    plt.close()
    return fig

# TODO: Change this to possible_states for all states.
def get_values_in_q(data, state, col_in_q='daily_return'):
    return list(data[data['state'] == state][col_in_q])

def generate_return_graph(report):
    alpha = round(100 * report['Avg Alpha'], 2)
    adj_alpha = round(100*report['Adj Alpha'], 2)
    percentile = round(report['Percentile (Against Random)'], 1) if report['Percentile (Against Random)'] else None
    alpha_color = 'green' if alpha >= 0 else 'red'
    adj_alpha_color = 'green' if adj_alpha >= 0 else 'red'
    title = report['Ticker'] + ' Return per Macro Unit Time'
    fig = plt.figure(figsize=(4, 4))
    plt.title(title)
    plt.xlabel('Macro Unit Time')
    plt.ylabel('Return + 1')
    plt.plot(report['markov_dts'], label='Markov Returns')
    plt.plot(report['buy_hold_dts'], label='Buy and Hold Returns')
    plt.text(x=0.75, y=0.94, s=f'Alpha: {alpha}', color=alpha_color, transform=plt.gca().transAxes, fontsize=8)
    plt.text(x=0.70, y=0.89, s=f'Adj Alpha: {adj_alpha}', color=adj_alpha_color, transform=plt.gca().transAxes, fontsize=8)
    plt.text(x=0.70, y=0.84, s=f'Percentile: {percentile}', color='black', transform=plt.gca().transAxes, fontsize=8)
    plt.legend()
    plt.close(fig)
    return fig

def generate_alpha_graph(report):
    alphas = [round(100* (markov - bh), 2) for markov, bh in zip(report['markov_dts'], report['buy_hold_dts'])]
    percentile = round(report['Percentile (Against Random)'], 1) if report['Percentile (Against Random)'] else None
    title = report['Ticker'] + ' Alpha per Macro Unit Time'
    fig = plt.figure(figsize=(4, 4))
    plt.title(title)
    plt.xlabel('Macro Unit Time')
    plt.ylabel('Alpha')
    plt.plot(alphas, label='Markov Alphas By Macro Unit Time')
    plt.text(x=0.70, y=0.94, s=f'Percentile: {percentile}', color='black', transform=plt.gca().transAxes, fontsize=8)
    plt.close(fig)
    return fig

def generate_pdf_report(reports, filename, file_prefix='report_outputs/report_graphs/', include_state_det_value_metrics=False, data=None):
    figures = generate_figs(reports, include_state_det_value_metrics=include_state_det_value_metrics, data=data)
    save_all_figures_to_single_pdf(figures, filename, file_prefix=file_prefix)

def partial_cov_map(reports):
    return
    #partial_df = calculate_aggregate_covariance(reports)
def save_transition_probabilities_to_pdf(report):
    df = report['Transition Probability Matrix']
    df = df.sort_index(axis=0).sort_index(axis=1)
    df = round(df * 100, 1)
    fig, ax =plt.subplots(figsize=(12,4))
    ticker = report['Ticker']
    plt.title(f'{ticker} Transition Probability Matrix')
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values,colLabels=df.columns,rowLabels=df.index,loc='center')
    plt.close(fig)
    return fig

def save_all_figures_to_single_pdf(figures, filename, file_prefix='report_outputs/report_graphs/'):
    """
    Save multiple Matplotlib figures in a single PDF file.

    Parameters:
    - figures: List of Matplotlib figure objects.
    - filename: Filename for the combined PDF (default: 'combined_figures.pdf').
    """
    if not os.path.exists(file_prefix):
        os.makedirs(file_prefix)
    filename = f'{file_prefix}{filename}.pdf'
    with PdfPages(filename) as pdf:
        for fig in figures:
            pdf.savefig(fig)
        print(f'Combined figures saved as {filename}')
def convert_to_json_serializable(obj):
    """
    Convert NumPy int64 to Python int to make it JSON serializable.
    """
    if isinstance(obj, np.int64):
        return int(obj)
    raise TypeError("Type not serializable")

def write_json_file(data_list, file_name, file_prefix='report_outputs/reports_jsons/'):
    """
    Write a list of dictionaries to a JSON file.

    Parameters:
    - data_list: List of dictionaries to be written to the file.
    - file_path: Path to the output JSON file.
    """
    if not os.path.exists(file_prefix):
        os.makedirs(file_prefix)
    file_path = f'{file_prefix}{file_name}.json'
    with open(file_path, 'w') as json_file:
        json.dump(data_list, json_file, indent=2, default=convert_to_json_serializable)  # indent for pretty formatting (optional)

def to_cov_matrix(cov_matrices, df_index, file_name=None):
    flattened_dfs = []
    df_array = cov_matrices
    for df in df_array:
        # Flatten the DataFrame. Here we're using `.values.flatten()` to create a single row array.
        # Note: Adjust this as necessary to match your desired form of 'flattening'.
        flattened_series = pd.Series(df.values.flatten())
        flattened_dfs.append(flattened_series)

    # Concatenate all flattened DataFrames into a single DataFrame
    # Each original DataFrame is now represented as a single row in the aggregate DataFrame
    aggregate_df = pd.concat(flattened_dfs, axis=1).transpose()
    aggregate_df.columns = cov_matrices[0].columns
    aggregate_df.index = df_index
    if file_name is not None:
        aggregate_df.to_csv(f'State_Determiner_Value_Reports/{file_name}.csv')
    return aggregate_df