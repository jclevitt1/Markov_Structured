# KELLY BOX
from scipy.optimize import root, brentq, root_scalar
from scipy.integrate import quad
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

RETURN_LOWER_BOUND = -0.05

def get_optimal_bet_next_unit(return_pdf, maximum_return=1, maxfev=3000, tol=1e-3, init_g=0.05):
    """
    Finds the optimal Kelly bet fraction S given a return PDF.

    Parameters:
    - return_pdf: The probability density function of returns.
    - maximum_return: The upper limit for integration (default is 10).

    Returns:
    - solution: The solution object from scipy.optimize.root containing the optimal S.
    """
    if return_pdf is None:
        return 0
    # Define the function to find the root of
    integral_function = lambda S: abs(integral_function_abstract(S, return_pdf, maximum_return))

    lower_S_bound = -1
    upper_S_bound = 1
    # Loop over the initial guesses
    root
    solution = root(integral_function, x0=init_g, tol=tol, method='df-sane')
    if solution.success:
        print(f"Success with initial guess:")
        print(solution)

    # Check if the solution was successful and print the result
    if solution.success:
        optimal_S = solution.x
        print(f"The optimal Kelly bet fraction S is: {optimal_S}")
    else:
        print("Root finding failed:", solution.message)

    return solution

def integral_function_abstract(S, return_pdf, maximum_return=0.05):
    """
    Computes the integral of p(x) * x / (1 + S * x) over the range [minimum_return, maximum_return].

    Parameters:
    - S: The Kelly bet fraction.
    - return_pdf: The probability density function of returns.
    - maximum_return: The upper limit for integration.

    Returns:
    - result: The value of the integral.
    """
    # if not 0 <= S <= 1:
    # return 0
    minimum_return = RETURN_LOWER_BOUND # Adjust as necessary for your distribution
    def integrand(x):
        return return_pdf(x) * x / (1 + S * x)

    result, error = quad(integrand, minimum_return, maximum_return, limit=10000)
    return result

# See notes in Green notebook lol
"""
Problem: We have that r >= -1, but p(r) > 0 for some r < -1.

Solution is to modify the PDF accordingly.
"""
def find_multiplier_modify_pdf(return_pdf, MIN, MAX):
    area_to_account, _ = quad(return_pdf, -np.inf, -MIN)
    area_to_be_added_to, _ = quad(return_pdf, MIN, MAX)
    multiplier = area_to_account / area_to_be_added_to + 1
    return multiplier

def plot_kelly(return_pdf, bounds=[-3, 3, 5000]):
    ss = np.linspace(bounds[0], bounds[1], bounds[2])
    fs = []
    for s in ss:
        fs.append(integral_function_abstract(s, return_pdf))
    plt.plot(ss, fs)

def fit_kde(data_series):
    kde_scipy = gaussian_kde(data_series, bw_method='silverman')
    return kde_scipy

def fit_kde_functions(filtered_data):
    state_kde_functions = {}
    for state in filtered_data.keys():
        d = filtered_data[state]
        if len(d) <= 1:
            kde_scipy = None
        else:
            kde_scipy = fit_kde(d['return'])
        state_kde_functions[state] = kde_scipy
    return state_kde_functions
