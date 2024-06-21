from temp.Distribution_U.Distribution import Distribution

class KernelDensityFitter():
    def __init__(self, distribution: Distribution):
        self.distribution = distribution

    def fit(self, distribution_dict=None):
        function_names, function_list = self.compute_fit()
        self.distribution.set_kernel_functions(function_names, function_list)
        # If distribution_dict is passed in, this is called from UniversalFitter, which we should update it with fitted info.
        if distribution_dict:
            fitted_var_map = { fitted_var_name: val for fitted_var_name, val in zip(fitted_var_names, vals) }
            distribution_dict['fitted_var_map'] = fitted_var_map

    """
    Returns the function list of the kernels.
    
    
    """
    def compute_fit(self):
        raise "Subclass should implement this function."

    """
    Since each defined distribution will have a fitter associated with it, it makes sense to make sure that the
    distribution passed in has the expected fitted_var_names. This is what perform_validations is meant to check.
    """
    def perform_validations(self, distribution: Distribution):
        raise "Subclass should implement this function."