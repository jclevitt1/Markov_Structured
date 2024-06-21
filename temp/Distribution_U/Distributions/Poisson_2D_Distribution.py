from temp.Distribution_U.Distribution import Distribution
import numpy as np

"""
Of course later on we should abstract to d dimensions.

Implementing 2d case to get some more intuition on rate-variant Poisson processes.

Scoring the Poisson distribution isn't straightforward actually. This is because Poisson gives probability of
"k" events occuring within a given region within some amount of time. This time interval necessarily MUST be equal to
the granularity of the given data. 

Having trouble interpretting what "K" will be in this context. Seems intuitive to set k=1 (i.e. we only need the price
to rise to 

Actually, to best leverage k here, we may need other framework actually. If neighboring areas have the same
probability for high K that the same area displaced has a much lower K, this is goood information. Specifically,
we would be concerned with comparing the rates between how the intensity "normally" changes versus how the intensity
changes in an anomaly. There's potentially interesting room for anomaly detection here.

This is only to get better intuition on how exactly the d-dim Poisson distribution would fit into my existing Dist
framework.

"""

class Poisson2dDistribution(Distribution):
    def __init__(self):
        necessary_hp_names = []
        necessary_fitted_var_names = ["k"]
        necessary_kernel_names = ["intensity"]
        necessary_var_names = ["volume", "daily_return"]
        # TODO: Update this to better reflect return. Should be -1 to ~5-10 ish. Distribute the extra p evenly.
        limits = [[-10, 10]]
        super().__init__("Poisson2d", self.pdf, limits, necessary_hp_names, necessary_fitted_var_names, necessary_var_names,
                         kernel_function_names=necessary_kernel_names)

    # Kernel functions may present issues with setting feature variables (all but return) as KDFs will not be
    # supplied enough arguments.
    # ALSO BIG TODO: Abstract the feature fitting here to be a vector instead of individual variables. This is much better framework to scale.
    def pdf(self, k, intensity, volume, r):
        # TODO: No internet on flight. Replace with actual PDF of Poisson.
        curr_intensity = intensity(volume, r)
        return curr_intensity ** k / np.factorial(k) * np.exp(-curr_intensity)

    def compute_area(self):
