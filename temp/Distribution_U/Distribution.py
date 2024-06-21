from temp.Distribution_U.DistributionWrapper import DistributionWrapper
from scipy.integrate import quad
"""
The Distribution Object. The foundation of the whole project- See Axiom 1.

Upon instantiation, the distribution object is meant to be as abstract as possible. If fitting a normal dist, for
instance, the mean and standard deviation are NOT specified upon instantiation. The idea of this is to be able to
control EVERY level of distribution fitting. So, what different "levels" of distribution fitting are there? To help this
abstraction, I have made four different types of variables to be fit: (Order is important)

1. Hyperparameters.
2. Fitted variables.
3. Fitted Kernel Density Functions.
4. Features (sometimes referred to as fitted_vars- this should be changed). Features must ALWAYS end with return.

Before any probability density function is used, it is assumed that the first (3) are fitted. That is, any
hyperparameters, kernel density functions, and fitted variables have been set. After the above three are set,
self.multivar_return_pdf is set by the DistributionWrapper (parent class) [or just return_pdf if only one feature]

This multivar_return_pdf is what will be scored in the ScorerBox.

A quick breakdown of each of the four variable abstractions:

1. Hyperparameters- self-explanatory. May be needed in multifractal distributions (less self-explanatory).
2. Fitted variables- "non-variable" variables. Examples would be using constant mean, std in Gaussian.

3. Fitted Kernel Density Functions- The need for this became clear when studying Poisson distributions.
Poisson distr's have equal probability with equal area in R^d. However, this is of course not how markets function,
especially with return as an axis. So, we need a varying Poisson rate wrt at least return, but may vary with other
features as well. This may require an additional abstraction for each distribution, something like "Kernel_Fitter".
Of course this is not needed for every fit distribution.
    EVERY kernel function must take the same feature arguments as the underlying PDF.

4. Features- MUST be present in the data. Currently considering restructuring this abstraction, because
feature names are validated as well, meaning that every time we wish to fit the same distribution to a different
feature we need a new distribution object.

For now, each distribution's PDF will be structured as follows:

def pdf(hyperparameters*, fitted_variables*, fitted_kernel_density_functions*, features*):
    some function that integrates to 1.
    
For the hyperparameters and the fitted variables, we require cutting the PDF each step. However, for the fitted
kernel density function, we do not need to cut

This is not scalable!! We NEED to solve this.

"""

class Distribution(DistributionWrapper):
    """
    Prerequisites.
    """
    def __init__(self, name, pdf, return_limits, necessary_hp_names, necessary_fitted_var_names, necessary_var_names, on_return=True, kernel_function_names=[]):
        if on_return:
            assert necessary_var_names[-1] == 'return' or necessary_var_names[-1] == 'daily_return', "Last variable name must be return."
        print(callable(pdf))
        # self.pdf is the pdf function.
        super().__init__(name, pdf, return_limits)
        self.necessary_hps_names = necessary_hp_names
        self.necessary_fitted_var_names = necessary_fitted_var_names
        self.necessary_var_names = necessary_var_names
        self.necessary_hps = { necessary_hp: None for necessary_hp in necessary_hp_names }
        self.necessary_fitted_vars = { necessary_fitted_var: None for necessary_fitted_var in necessary_fitted_var_names}
        self.necessary_vars = { necessary_var: None for necessary_var in necessary_var_names }
        self.kernel_function_names = kernel_function_names
        self.kernel_functions = { kernel_function_name: None for kernel_function_name in kernel_function_names }

    """
    Some distributions may have a PDF that is dependent on some other function.
    
    For now, the largest one to consider is Poisson processes which are not equally distributed amongst some given
    subarea of R^n. I.e. we wish to vary the density/rate of occurrence of a few points within a given region.
    
    Poisson R^2 is like playing darts without a center target- every area has an equal chance of containing some
    points, without dependency on where the area is. This is of course not true with returns.
    
    This function does not do the calculation of the kernel function, but rather is given the kernel function name
    and its corresponding behavior in kern_dict_description.
    
    
    Let some distribution need k kernel functions to be fit, namely ker_0, ker_1, ..., ker_k.
    The kern_descriptions list is constructed in the following manner (list of dictionaries):
    {
        'ker_1_name': f_1 (lambda_1),
        f_2 (lambda_2), ... f_k
    }
    
    Note that the ordering of arguments is not validated here. Only validation planned for this function is to include
    a check that the number of arguments specified is correct.
    """
    def set_kernel_functions(self, kern_names, kern_descriptions):
        if not self.kernel_function_names:
            print(f"No fitted functions for distrbituion {self.name}. Short circuiting.")
            return
        kernel_functions = self.perform_kernel_validations(kern_names, kern_descriptions)
        self.configure_kernel_pdf(kernel_functions)
        return

    def perform_kernel_validations(self, kern_names, kern_descriptions):
        assert self.kernel_function_names == kern_names, "All kernel functions must be fit."
        assert len(kern_descriptions.values) == len(kern_names), "Number of kernel function behaviors does not match number of kernel names."
        kernel_functions = []
        for kern_name in kern_names:
            # The kernel multivariable function should less than or equal to the number of feature/data args.
            k = kern_descriptions[kern_name]
            assert len(inspect.signature(k).parameters) == len(self.necessary_var_names), "Kernel args must be equal to total feature args."
            kernel_functions.append(k)
        return kernel_functions

    """
    First stage in specifying the PDF down from the many abstract variables. Setting hyperparameters.
    
    Set the hyperparameters of the pdf defined in init.
    Uses self.configure_hyperparam_pdf to generate self.hp_configured_pdf in order to eventually
    have a single PDF that only depends on return.
    """
    def set_hps(self, hps, vals):
        assert len(hps) == len(self.necessary_hps_names), "Setting hyperparams did not match object's record."
        for i, hp in enumerate(hps):
            assert hp == self.necessary_hps_names[i], "Names and order of HPs must match."
            self.necessary_hps[hp] = vals[i]
        self.configure_hyperparam_pdf(*vals)

    def set_fitted_vars(self, fitted_var_names, vals):
        assert len(fitted_var_names) == len(self.necessary_fitted_vars), "Setting fitted variables did not match object's record."
        for i, var in enumerate(fitted_var_names):
            assert var == self.necessary_fitted_var_names[i], 'Names and order of variables must match'
            self.necessary_vars[var] = vals[i]
        self.configure_multivar_return_pdf(*vals)

    """
    Second stage in specifying the PDF down from the many abstract varaibles. HPs have been set, and now we need
    to set the value of our current variables.
    
    This will generate self.return_pdf, which is only dependent on any given return value for a PDF value.
    
    Since 
    """
    def set_vars(self, var_names, vals):
        if self.return_pdf:
            print("All variables already set (likely not fitting any other features besides return. Short-circuiting.")
            return
        assert len(var_names) == len(self.necessary_vars_names) - 1, "Setting variables did not match object's record."
        assert "daily_return" not in var_names, "Return should not be set in this function."
        assert "return" not in var_names, "Return should not be set in this function"
        for i, var in enumerate(var_names):
            # Commenting the below out, as see
            # assert var == self.necessary_vars_names[i], "Names and order of variables must match."
            self.necessary_vars[var] = vals[i]
        self.configure_return_pdf(*vals)

    def check_pdf_ready(self):
        if not self.return_pdf:
            raise "Return PDF is not yet generated. Not yet ready."
        return

    def pdf_on_return(self, r):
        self.check_pdf_ready()
        return self.return_pdf(r)

    """
    Given the current (only) return dependent PDF, gets the probability that return will be in between r_left and
    r_right.
    """
    def get_probability(self, r_left, r_right):
        self.check_pdf_ready()
        result, error = quad(self.return_pdf, r_left, r_right)
        return result, error

    def cdf(self, max_r):
        return self.get_probability(-1, max_r)