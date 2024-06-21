import inspect
from scipy.integrate import nquad
from functools import partial
import numpy as np

"""
DistributionWrapper.

Is the main abstraction of a "Distribution." This object is independent of knowledge of hyperparameters, i.e.
it has no clue which variables are hyperparameters or variables of a passed in PDF. This is known at a level below this,
the Distribution layer. However, this does have hyperparameter/variable related functions that all distributions can
call.

Originally, a PDF is given as a function of hyperparameters, fixed variables, other features, and return.
The DistributionWrapper is ultimately responsible for cutting this down by each layer (though we are primarily
interested the most in two: fixed variable + return pdf and return pdf.

The below is slightly outdated since we have added fitted variables to distributions, but same logic should apply.

1. set_pdf --> validations are not done on the first PDF set without configured hyperparameters.
The PDF that is passed in to the function above should be structured as follows:
f(hyperparameters*, variables*, "return")

2. configure_hyperparam_pdf --> takes in a list of hyperparameters, passes it into f to come up with a new partial
function of f that should be equivalent to the following
f*(variables*, "return")
Ensures that this is a valid PDF, then sets this new partial function equal to self.hp_configed_pdf

3. configure_return_pdf --> same as above, but takes in a list of variables and validates resulting to get
self.return_pdf, dependent on only one variable, i.e. return.
"""
class DistributionWrapper:
    def __init__(self, name, pdf, limits):
        self.name = name
        self.return_limits = limits
        self.pdf = self.set_pdf(pdf, limits, do_validations=False)

    """
    PDF is a function of n variables.
    This function verifies that pdf is a valid PDF, and sets the distribution's pdf to this.
    
    Ideally, later on we should add a restriction that r >= -1 but for now it is fine without.
    Have the option to skip validations for when originally the pdf is passed in with abstract hyperparameters.
    
    Note that limits are integration bounds only on variables + return, NOT on hyperparameters.
    """
    def set_pdf(self, pdf, limits, do_validations=True):
        self.num_pdf_params = len(inspect.signature(pdf).parameters)
        if do_validations:
            self.validate_pdf(pdf, limits)
        self.pdf = pdf
        print("PDF set successfully.")
        return pdf

    def _cut_pdf(self, pdf, *params):
        fixed_pdf = partial(pdf, *params)
        return fixed_pdf

    def configure_hyperparam_pdf(self, *hyperparams):
        hp_configed_pdf = self._cut_pdf(self.pdf, *hyperparams)
        print(inspect.signature(hp_configed_pdf))
        # len(hyperparams): takes the limits of integration that do not include the hyperparams. We should probably
        # remove this all together.

        # The below line is leftover from when limits included all variables.
        # self.validate_pdf(hp_configed_pdf, self.limits)
        self.hp_configured_pdf = hp_configed_pdf

    def configure_kernel_pdf(self, kernel_functions):
        if not self.multivar_return_pdf:
            raise "Multivariable feature/kernel PDF should be configured at this point in fitting process."
        self.multivar_return_pdf = self._cut_pdf(self.multivar_return_pdf, *kernel_functions)

    """
    Configures PDF to be a function of only the dependent features and return.
    """
    def configure_multivar_return_pdf(self, *fitted_variables):
        multivar_return_pdf = self._cut_pdf(self.hp_configured_pdf, *fitted_variables)
        # TODO: Add the following line in when DistributionWrapper takes in integration limits on other features
        # TODO: besides return.
        # self.validate_pdf(multivar_return_pdf, self.return_limits)

        # If the number of arguments of the function is 1, this necessarily means the PDF is only return dependent.
        # I.e. we are not fitting to another feature.
        if (len(inspect.signature(multivar_return_pdf).parameters) == 0):
            raise "PDF arg length should not be 0."
        if (len(inspect.signature(multivar_return_pdf).parameters) == 1):
            print("validating PDF ...")
            self.validate_pdf(multivar_return_pdf, self.return_limits)
            self.return_pdf = multivar_return_pdf
        else:
            print(f'args > 1. Skipping validation on pdf.')
        self.multivar_return_pdf = multivar_return_pdf

    """
    Needs update.
    """
    def configure_return_pdf(self, *variables):
        return_configed_pdf = self._cut_pdf(self.hp_configured_pdf, *variables)
        self.validate_pdf(return_configed_pdf, self.return_limits)
        self.return_pdf = return_configed_pdf

    def validate_pdf(self, pdf, limits):
        print(f"validating PDF ...")
        result, error = nquad(pdf, limits)
        if not np.isclose(result, 1, atol=1e-3):
            raise ValueError("Provided function does not integrate to 1 over the specified range, integral was {}".format(result))
        return
