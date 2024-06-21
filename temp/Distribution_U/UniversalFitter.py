import os
from temp.Distribution_U.HP_Setter.HP_Setter import HP_Setter
from temp.config import DISTRIBUTIONS_U_PATH
import pandas as pd

# This is its own package to solve: https://stackoverflow.com/questions/11536764/how-to-fix-attempted-relative-import-in-non-package-even-with-init-py
def fit_universal(filtered_data: pd.DataFrame, return_col='daily_return', test_override_path=None):
    """
    The logic below is mostly right, but implied return type is wrong. Return type is a List<List<Dictionaries>>, where
    each 1D element of the first list represents a different distribution, each 2nd dimensional element of list
    represents some hyperparameter, fitted combination of that distribution, and each dictionary contains the actual
    data of that list as described below.

    Logic:
    1. Get all implemented distributions.
    2. For each distribution,
        A. For each hyperparameter element of hyperparameter list (corresponding to that distribution):
            I. Set HP's of the distribution to element.
            II. Fit the distribution with the corresponding Distribution_Fitter.
            III. This should put the distribution object in an end state to have attribute
                    self.multivar_return_pdf --> PDF dependent on only dependent features, as well as return.
            IV. Have some dict with the following structure:
            {
                'distribution_type': distribution_type,
                'distribution': distribution_obj,
                'hp_map': {'hp_name1': hp_val1, ..., }
                'fitted_var_maps': {'fitted_var_name1': fitted_var_val1, ..., }
                # Directly from distribution object- distribution.variables.
                'pdf_param_names': []
            }
            V. Append this dictionary to ongoing list.
    3. Return the constructed list.
    """
    assert 'state' in filtered_data.columns, "No STATE feature passed in. Please ensure data is stateful."
    assert return_col in filtered_data.columns, "Please ensure a RETURN_COL (or column of interest) is present in data."
    # At this point, the filtered_data should only contain a single state.
    assert filtered_data['state'].nunique() == 1, "Data with only a SINGLE state should be passed in."
    distribution_names = _get_distribution_names(test_override_path=test_override_path)
    full_distribution_info_list = []
    for distribution_name in distribution_names:
        full_distribution_info_list.append(fit_distributions_all_hp_combinations(distribution_name))
    return full_distribution_info_list

def fit_distributions_all_hp_combinations(filtered_data, distribution_name):
    distribution_class = _get_distribution_class(distribution_name)
    # Using hp_setter_and_builder since the hp setter instantiates many of the distribution objects within its own
    # right, though this should probably be changed later.
    hp_setter_and_builder = HP_Setter(distribution_name, distribution_class)
    # Dictionary of all fitted HP distributions. Already has distribution name, distribution objects (unfitted), hpmap.
    # Needs fitted var map.
    list_hp_set_distributions = hp_setter_and_builder.construct_necessary_distribution_objects()
    for distr_dict in list_hp_set_distributions:
        distribution_fitter_class = _get_distribution_fitter_class(distribution_name)
        distribution_fitter_inst = distribution_fitter_class(filtered_data, distr_dict['distribution'])
        distribution_fitter_inst.fit(distribution_dict=distr_dict)
        # Final update to the dictionary
        distr_dict['pdf_param_names'] = distr_dict['distribution'].necessary_var_names
    return list_hp_set_distributions

def _get_distribution_names(test_override_path=None):
    if test_override_path:
        DISTRIBUTIONS_U_PATH = test_override_path
    directory = f'{DISTRIBUTIONS_U_PATH}/Distributions'
    # Initialize an empty list to store the extracted names
    names = []

    # List all files in the specified directory
    for filename in os.listdir(directory):
        # Check if the file follows the expected pattern
        if filename.endswith("_Distribution.py"):
            # Extract the part of the filename between 'Distributions/' and '_Distribution.py'
            name = filename[:-len("_Distribution.py")]
            names.append(name)
    return names

def _get_class(module_name, class_name):
    module = __import__(module_name, fromlist=[class_name])
    # Get the class from the module
    dist_class = getattr(module, class_name)
    return dist_class

def _get_distribution_class(distribution_name):
    """
    This function dynamically imports the corresponding Python module
    and instantiates the class named '{X}_Distribution' where X is the distribution name.
    """
    # Construct the module name and the full path to the class
    module_name = f"temp.Distribution_U.Distributions.{distribution_name}_Distribution"
    class_name = f"{distribution_name}_Distribution"
    return _get_class(module_name, class_name)

def _get_distribution_fitter_class(distribution_name):
    """
    This function dynamically imports the corresponding Python module
    and instantiates the class named '{X}_Distribution' where X is the distribution name.
    """
    # Construct the module name and the full path to the class
    module_name = f"temp.Distribution_U.Distribution_Fitters.{distribution_name}_Distribution_Fitter"
    class_name = f"{distribution_name}_Distribution_Fitter"
    return _get_class(module_name, class_name)
