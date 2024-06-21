from temp.Distribution_U.Distribution import Distribution
import numpy as np

class Standard_Log_Gauss_Distribution(Distribution):
    def __init__(self):
        necessary_hp_names = []
        necessary_fitted_var_names = ["mean", "std"]
        necessary_var_names = ["daily_return"]
        # TODO: Update this to better reflect return. Should be -1 to ~5-10 ish. Distribute the extra p evenly.
        limits = [(-1, np.inf)]
        super().__init__("Standard_Log_Gauss", self.pdf, limits, necessary_hp_names, necessary_fitted_var_names, necessary_var_names)

    """
    Gives return value (un-transformed into log, r = 0 for no change, r + 1 for pre-transformed (before log).
    """
    def pdf(self, m, std, r):
        if r < -1:
            return 0
        r += 1
        # TODO: Make everything <= -1 0 probability and weight the rest of the function accordingly
        # To weight the rest of the function, simply take missing area from -1 to -inf and make sure the integral from
        # min_return to inf adds back this area.
        coef = 1 / (r * std * np.sqrt(2 * np.pi))
        exp_term_pt1 = ((np.log(r) - m) / std) ** 2
        exp_term = np.exp(-0.5 * exp_term_pt1)
        pdf_val = coef * exp_term
        return pdf_val
