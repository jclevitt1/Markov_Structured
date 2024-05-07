import random
import numpy as np
import json

"""
NEEDS TO BE RESTRUCTURED.

For now, this class will only simulate the results of a single set of return rates and their corresponding probabilites.

What does this mean?
At this point, we assume we have a model that, in some way or another (it may be a result of ensemble), outputs the
following parameters: return_rates of the next day, and their corresponding probabilities.

As we know, the question of "should I decide to invest given these parameters? Is actually more complex than it seems.

Besides personal preference, the answer to this question is the EXACT SAME answer to the parallel question:
If I made the same decision, given the same parameters, every day moving forward to infinity, would I be satisfied
with the result?

The extremely basic answer is yes if it diverges to infinity, no if it converges to 0. However,
the speed of divergence of course matters here. Also, the variance in the first n trials matters as well. The amount
of times you end up on top of course also matters.

This file is meant to answer the above question, by having some SUBSTITUTE_FOR_INFINITY variable which plays out the
following scenario: 

Assume investment is made, and probabilities and rates given are accurate. Then:
    1. Simulate SUBSTITUTE_FOR_INFINITY number of days with the exact same set of return rates and probabilities.
    2. Perform (1) until we have done so NUM_SIM times.
    3. Record results and summary statistics of the performance.
    
Statistics we should record:
1. Count of profitable runs.
2. Averages from 0-P10, 0-P20, ...-P90 level. (and of course full avg)
3. Count of runs with < 80% of portfoilo value at end of run.
4. Count of runs with < 70% of portfolio value at end of run.

Return rates should not be % gain or loss, but should be the multiplier (i.e. 1 + gain)
"""
def simulate(return_rates, probabilities, SUBSTITUTE_FOR_INFINITY=10000, NUM_SIMS=1000):
    results = [0 for i in range(NUM_SIMS)]
    for j in range(NUM_SIMS):
        p = 1
        for i in range(SUBSTITUTE_FOR_INFINITY):
            todays_return = random.choices(return_rates, weights=probabilities)[0]
            p *= todays_return
        results[j] = p
    results = sorted(results)
    return results

"""
Collects stats on the above simulation.

There should be a better way to collect this later. Probably better to just have raw data and a processor for this instead.
Fine for now.
"""
def collect_stats(results, save_to_json=None, SUBSTITUTE_FOR_INFINITY=10000, NUM_SIMS=1000):
    profitable_arr = [1 if result >= 1 else 0 for result in results]
    stats = {}
    stats['NUM_DAYS'] = SUBSTITUTE_FOR_INFINITY
    stats['NUM_SIMS'] = NUM_SIMS
    stats['avg Profit when Profit'] = np.mean([result for result in results if result >= 1])
    stats['avg Loss when Lost'] = np.mean([result for result in results if result < 1])
    stats['avg'] = np.mean(results)
    stats['std'] = np.std(results)
    stats['profitablePercent'] = (sum(profitable_arr) / len(results)) * 100
    for i in range(90, 0, -10):
        index = int(i / 100 * len(results))
        stats['>' + str(i) + '%LOSS Percent'] = sum([1 if result <= i / 100 else 0 for result in results]) / len(results) * 100
        stats['avgT' + str(i)] = np.mean(results[:index])
        stats['stdT' + str(i)] = np.std(results[:index])
        stats['profitablePercentT' + str(i)] = (sum(profitable_arr[:index]) / len(profitable_arr[:index])) * 100

    if save_to_json:
        with open(save_to_json, 'w') as json_file:
            json.dump(stats, save_to_json)
    return stats