from temp.Distribution_U.Distribution import Distribution
from temp.Distribution_U.Distributions.Standard_Log_Gauss_Distribution import Standard_Log_Gauss_Distribution
from temp.Distribution_U.Distribution_Fitters.Distribution_Fitter import Distribution_Fitter
import numpy as np
import pandas as pd

class Standard_Log_Gauss_Distribution_Fitter(Distribution_Fitter):
    # Each constructor for each distribution should only have the following two lines. Validation done by parent.
    def __init__(self, filtered_data: pd.DataFrame, distribution: Distribution, return_col='daily_return'):
        expected_necessary_fitted_var_names = ["mean", "std"]
        filtered_data['log_return'] = np.log(filtered_data[return_col] + 1)
        self.log_return_col = 'log_return'
        super().__init__(filtered_data, distribution, expected_necessary_fitted_var_names, return_col='log_return')

    """
    Returns fitted_var_names, values to set to the distribution.
    
    Fit is implemented by parent class. This is not meant to be called other than by the Parent Fitter class.
    """
    def compute_fit(self):
        log_return_col = self.filtered_data[self.log_return_col]
        log_mean = np.mean(log_return_col)
        log_std = np.std(log_return_col)
        print(f'Mean: {log_mean}')
        print(f'Std: {log_std}')
        return self.expected_necessary_fitted_var_names, [log_mean, log_std]

    """
    Since each defined distribution will have a fitter associated with it, it makes sense to make sure that the
    distribution passed in has the expected fitted_var_names. This is what perform_validations is meant to check.
    """
    def perform_validations(self, distribution: Distribution):
        assert type(distribution) is Standard_Log_Gauss_Distribution, "DISTRIBUTION IS NOT OF EXPECTED TYPE."
        assert distribution.necessary_fitted_var_names == self.expected_necessary_fitted_var_names, \
            "Necessary fitted variable names do not match."
        return