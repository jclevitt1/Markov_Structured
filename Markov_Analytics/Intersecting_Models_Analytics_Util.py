from collections import defaultdict

# Inspiration for this model is given below the function.
def get_pos_neg_combo_records(data, state1_col, state2_col, col_in_question='daily_return', L=25, K=1):
    std_name = 'analysis_STD_L' + str(L)
    data[std_name] = data[col_in_question].rolling(window=L).std()
    # number of times the threshhold is crossed and the date at which it is crossed.
    positive_records_over_b = defaultdict(lambda:[0, []])
    negative_records_over_b = defaultdict(lambda:[0, []])
    for i in range(len(data)):
        # placeholder
        B = 2 * K * data.iloc[i][std_name] #let's shift to moving 2 * moving SD.
        if data.iloc[i][col_in_question] > B:
            s1, s2 = data.iloc[i][state1_col], data.iloc[i][state2_col]
            state_ind = f'{s1}.{s2}'
            positive_records_over_b[state_ind][0] += 1
            positive_records_over_b[state_ind][1].append(data.index[i])
            # do something with s1, s2
        elif data.iloc[i][col_in_question] < -B:
            s1, s2 = data.iloc[i][state1_col], data.iloc[i][state2_col]
            state_ind = f'{s1}.{s2}'
            negative_records_over_b[state_ind][0] += 1
            negative_records_over_b[state_ind][1].append(data.index[i])

    positive_state_combos = set(positive_records_over_b.keys())
    negative_state_combos = set(negative_records_over_b.keys())

    positive_records = {key: [] for key in positive_state_combos}
    negative_records = {key: [] for key in negative_state_combos}

    for i in range(len(data)):
        s1 = data.iloc[i][state1_col]
        s2 = data.iloc[i][state2_col]
        intersecting_state = f'{s1}.{s2}'
        if intersecting_state in positive_state_combos:
            val = data.iloc[i][col_in_question]
            date = data.index[i]
            r_dict = {'date':date, col_in_question:val}
            positive_records[intersecting_state].append(r_dict)
        if intersecting_state in negative_state_combos:
            val = data.iloc[i][col_in_question]
            date = data.index[i]
            r_dict = {'date':date, col_in_question:val}
            negative_records[intersecting_state].append(r_dict)
    return positive_records, positive_records_over_b, negative_records, negative_records_over_b

"""
Now we have potential to have two intersecting Markov models. Best idea now is to think about
exactly how we may identify "powerful" combination of states.

By "powerful" combination of states, we mean a combination of states that strongly indicates and seems
to have some causal relation with a dramatic growth of drop in return the following unit in time.

Given this problem space, and given we can never with full certainty identify fully causal states, our
best bet is identifying areas of high correlation.

DEFINE some lower bound, B, such that when the return of the asset is > B, record the combination in some
dictionary, and keep count of how many times such a combination leads to a growth in price. Also keep track
in a second dictionary, how many times this combination pops up. In fact, for this second dictionary, list all the times the combination comes up, and the returns of the next day associated with that combination (just in case it comes close to B but does not breach, B itself for that time, and the date (in case there was a yearly anomaly such as 2020). This way, we can identify if there are any patterns with the returns for the stock.

Of course here, we should keep in mind:
1. number of instances of the combination
2. number of instances where the combination causes the asset to breach threshhold B.
3. other returns of the combination, given this time period.

There are a number of ways to define B. Flushing out some ideas here:
1. Constant threshhold based on previous deviation in return.
2. Moving B with some multiple times the deviation.

The definition of B is not insanely important since we will have all the returns for every time the combination pops up as well as the year. We can do more analysis on this, rather than focus on tweaking B.
"""