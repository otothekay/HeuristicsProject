import pandas as pd

from Zombie_Starfish import *
import pandas as pd

# best result found with value of 160
#initial_starfish = [7, 10, 9, 13, 1, 14, 0, 2, 12, 8, 4, 11, 3, 6, 5]

# want to collect time found, generation found, optimality gap for each run
datasets = [tsp_lab_data, tsp_data_bays29, tsp_data_eil51, tsp_data_KroA100]
optimals = [lab_data_optimal, tsp_data_bays29_optimal, tsp_data_eil51_optimal, tsp_data_KroA100_optimal]
runs_per_dataset = 3

results_df = None
filename = 'Zombie_Starfish_run_data.csv'

for index, (dataset, optimal_value) in enumerate(zip(datasets[1:], optimals[1:])):
    for run in range(0, runs_per_dataset):
        print('')
        print(f'Run {run} for dataset {index}')

        model = ZombieStarfish(legs_per_starfish=5,
                               maximum_population=50,
                               maximum_generations=50,
                               max_time=20,                      #minutes
                               tsp_data=dataset,
                               test_optimal=optimal_value,
                               initial_starfish=None
                               )

        model.Unleash_Zombie_Starfish()
        event_data = model.event_log
        event_data['index'] = [index] * len(event_data['time'])
        event_data['run'] = [run] * len(event_data['time'])

        if results_df is None:
            results_df = pd.DataFrame(columns=event_data.keys())

            data_df = pd.DataFrame(data=event_data)
            copy = results_df.copy()
            results_df = pd.concat([copy, data_df], axis=0)

        else:
            data_df = pd.DataFrame(data=event_data)
            copy = results_df.copy()
            results_df = pd.concat([copy, data_df], axis=0)

        print('')

results_df.to_csv(filename)