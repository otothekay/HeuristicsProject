import pandas as pd

from Zombie_Starfish import *

# best result found with value of 160
#initial_starfish = [7, 10, 9, 13, 1, 14, 0, 2, 12, 8, 4, 11, 3, 6, 5]

datasets = [tsp_data_bays29, tsp_data_eil51, tsp_data_KroA100]

# want to collect time found, generation found, optimality gap for each run

model = ZombieStarfish(legs_per_starfish=5,
                        maximum_population=20,
                        maximum_generations=10,
                        # initial_starfish= initial_starfish,
                        tsp_data=tsp_data_eil51
                        )
print('model loaded')

model.Unleash_Zombie_Starfish()
results = model.ranked_population_dict
results_df = pd.DataFrame(results)