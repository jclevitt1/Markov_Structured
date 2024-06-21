from temp.Distribution_U.Distribution import Distribution
import numpy as np

class Gauss_Distribution(Distribution):
    def __init__(self):
        necessary_hp_names = []
        necessary_fitted_var_names = ["mean", "std"]
        necessary_var_names = ["daily_return"]
        # TODO: Update this to better reflect return. Should be -1 to ~5-10 ish. Distribute the extra p evenly.
        limits = [[-10, 10]]
        super().__init__("Gauss", self.pdf, limits, necessary_hp_names, necessary_fitted_var_names, necessary_var_names)

    def pdf(self, m, std, r):
        # TODO: Make everything <= -1 0 probability and weight the rest of the function accordingly
        # To weight the rest of the function, simply take missing area from -1 to -inf and make sure the integral from
        # min_return to inf adds back this area.
        coef = 1 / (std * np.sqrt(2 * np.pi))
        exp_term = -0.5 * ((r - m) / std) ** 2
        pdf_val = coef * np.exp(exp_term)
        return pdf_val
