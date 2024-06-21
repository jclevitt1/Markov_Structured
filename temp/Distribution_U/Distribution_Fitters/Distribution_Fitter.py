from temp.Distribution_U.Distribution import Distribution
import pandas as pd

class Distribution_Fitter():
    def __init__(self, filtered_data: pd.DataFrame, distribution: Distribution, expected_necessary_fitted_var_names, return_col='daily_return'):
        self.filtered_data = filtered_data
        self.distribution = distribution
        self.return_col = return_col
        self.expected_necessary_fitted_var_names = expected_necessary_fitted_var_names
        self.perform_validations(distribution)

    def fit(self, distribution_dict=None):
        fitted_var_names, vals = self.compute_fit()
        self.distribution.set_fitted_vars(fitted_var_names, vals)
        # If distribution_dict is passed in, this is called from UniversalFitter, which we should update it with fitted info.
        if distribution_dict:
            fitted_var_map = { fitted_var_name: val for fitted_var_name, val in zip(fitted_var_names, vals) }
            distribution_dict['fitted_var_map'] = fitted_var_map


    """
    Returns fitted_var_names, values to set to the distribution.
    """
    def compute_fit(self):
        raise "Subclass should implement this function."

    """
    Since each defined distribution will have a fitter associated with it, it makes sense to make sure that the
    distribution passed in has the expected fitted_var_names. This is what perform_validations is meant to check.
    """
    def perform_validations(self, distribution: Distribution):
        raise "Subclass should implement this function."