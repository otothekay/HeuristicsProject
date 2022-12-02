from FireflyTSP import *
import pandas as pd
from Zombie_Starfish import *

datasets = [tsp_lab_data, tsp_data_bays29, tsp_data_eil51, tsp_data_KroA100]
optimals = [lab_data_optimal, tsp_data_bays29_optimal, tsp_data_eil51_optimal, tsp_data_KroA100_optimal]
runs_per_dataset = 3

results_df = None
filename = 'Firefly_Algorithm_run_data.csv'

for index, (dataset, optimal_value) in enumerate(zip(datasets[:2], optimals[:2])):
    for run in range(0, runs_per_dataset):
        print('')
        print(f'Run {run} for dataset {index}')

        model = FireflyTSP(
            population_size=10,
            gamma=1,                                #gamma not built in yet
            maximum_generations=10,                 #max gens not built in yet
            max_time=10,  # minutes                 #max_time not built in yet
            tsp_data=dataset,
            test_optimal=optimal_value,
                            )

        population, avg_cost, best_cost, best_solution = model.firefly_heuristic()

        print(population)
        print(best_cost)
        print(best_solution)