from temp.Distribution_U.Distribution import Distribution
from temp.Distribution_U.Distributions.Gauss_Distribution import Gauss_Distribution
from temp.Distribution_U.Distribution_Fitters.Distribution_Fitter import Distribution_Fitter
import numpy as np
import pandas as pd

class Gauss_Distribution_Fitter(Distribution_Fitter):
    # Each constructor for each distribution should only have the following two lines. Validation done by parent.
    def __init__(self, filtered_data: pd.DataFrame, distribution: Distribution, return_col='daily_return'):
        expected_necessary_fitted_var_names = ["mean", "std"]
        super().__init__(filtered_data, distribution, expected_necessary_fitted_var_names, return_col=return_col)

    """
    Returns fitted_var_names, values to set to the distribution.
    
    Fit is implemented by parent class. This is not meant to be called other than by the Parent Fitter class.
    """
    def compute_fit(self):
        return_col = self.filtered_data[self.return_col]
        mean = np.mean(return_col)
        std = np.std(return_col)
        return self.expected_necessary_fitted_var_names, [mean, std]

    """
    Since each defined distribution will have a fitter associated with it, it makes sense to make sure that the
    distribution passed in has the expected fitted_var_names. This is what perform_validations is meant to check.
    """
    def perform_validations(self, distribution: Distribution):
        assert type(distribution) is Gauss_Distribution, "DISTRIBUTION IS NOT OF EXPECTED TYPE."
        assert distribution.necessary_fitted_var_names == self.expected_necessary_fitted_var_names,\
            "Necessary fitted variable names do not match."
        return