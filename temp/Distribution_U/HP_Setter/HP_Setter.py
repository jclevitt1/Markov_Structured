import json
from typing import Type
from temp.Distribution_U.Distribution import Distribution
from temp.config import DISTRIBUTIONS_U_PATH

class HP_Setter():
    def __init__(self, distribution_name, distribution_class: Type[Distribution]):
        self.distribution_name = distribution_name
        self.distribution_class = distribution_class
        hp_info_file_name = self._construct_file_name(distribution_name)
        with open(hp_info_file_name, 'r') as file:
            data = json.load(file)
        self.hp_names = data['hp_names']
        # 2D array containing all combinations of hyperparameters to iterate over.
        # Eventually we may not wish to store this in JSON, but for now this is fine.
        self.hp_vals_list = data['hp_vals_list']
        self.construct_necessary_distribution_objects()

    def _construct_file_name(self, distribution_name):
        # Gauss_Distribution_HPInfo.json
        return f'{DISTRIBUTIONS_U_PATH}/HP_Setter/HPInfo/{distribution_name}_Distribution_HPInfo.json'

    """
    For simplicity sake, for now, for each HP, we create a new object. Each of these objects will be used and then have
    their distributions fitted separately. This is mostly to track any data needed after all is said and done.
    
    Also, this shouldn't be the case (since they are HP's), but if any of the fitted variables change at all with hyper
    parameters it would strictly be a mistake to fit the distribution only once for varying hyperparams. Unsure of this
    assumption so maintaining this order for now.
    
    If we later find that this data is not needed, then we can modify this impl.
    Returns a list of dictionaries, each dictionary containing:
    
    1. ['distribution'] : Distribution object with fitted hyperparameters.
    2. ['hp_names'] : Unnecessary for each element, but keeping around for ease for now.
    3. ['hp_vals'] : The hyperparameter values for each of the names given above.
    """
    def construct_necessary_distribution_objects(self):
        # Elements of this list
        all_dists_and_hps = []
        for hp_val_set in self.hp_vals_list:
            curr_dist = self.distribution_class()
            curr_dist.set_hps(self.hp_names, hp_val_set)
            hp_map = { hp_name: hp_val for hp_name, hp_val in zip(self.hp_names, hp_val_set)}
            d = {
                'distribution_name': self.distribution_name,
                'distribution': curr_dist,
                'hp_map': hp_map
            }
            all_dists_and_hps.append(d)
        return all_dists_and_hps
