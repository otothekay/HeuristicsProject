import pandas as pd

from Zombie_Starfish import *

# best result found with value of 160
#initial_starfish = [7, 10, 9, 13, 1, 14, 0, 2, 12, 8, 4, 11, 3, 6, 5]

# want to collect time found, generation found, optimality gap for each run
datasets = [tsp_lab_data, tsp_data_bays29, tsp_data_eil51, tsp_data_KroA100]
optimals = [lab_data_optimal, tsp_data_bays29_optimal, tsp_data_eil51_optimal, tsp_data_KroA100_optimal]
runs_per_dataset = 3

for index, (dataset, optimal_value) in enumerate(zip(datasets, optimals)):
    for run in range(1, runs_per_dataset+1):
        print(f'Run {run} for dataset {index + 1}')

        model = ZombieStarfish(legs_per_starfish=5,
                               maximum_population=50,
                               maximum_generations=50,
                               max_time=20,                      #minutes
                               tsp_data=dataset,
                               test_optimal=optimal_value,
                               initial_starfish=None
                               )

        model.Unleash_Zombie_Starfish()
        print('')
